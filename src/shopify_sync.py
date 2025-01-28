import shopify
from typing import Dict, Any, List
import os
import json
import time
import requests
from loguru import logger
from dotenv import load_dotenv
from datetime import datetime, timedelta
from .database import Database

load_dotenv()

class ShopifySync:
    def __init__(self):
        """Initialize Shopify API connection"""
        self.shop_url = os.getenv('SHOPIFY_SHOP_URL')
        self.access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
        self.api_version = '2024-01'
        
        # REST API setup for individual product operations
        shopify.ShopifyResource.set_site(f"https://{self.shop_url}/admin/api/{self.api_version}")
        shopify.ShopifyResource.set_headers({'X-Shopify-Access-Token': self.access_token})
        
        # GraphQL API setup for bulk operations
        self.graphql_url = f"https://{self.shop_url}/admin/api/{self.api_version}/graphql.json"
        self.headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token
        }

    def _create_product(self, product_data: Dict[str, Any]) -> bool:
        """Create a new product in Shopify using GraphQL"""
        try:
            # Önce ürünü REST API ile oluşturalım
            shopify_product = shopify.Product()
            shopify_product.title = product_data.get('title') or f"INSIZE {product_data['sku']}"
            shopify_product.body_html = product_data.get('description', '')
            shopify_product.vendor = "INSIZE"
            shopify_product.product_type = product_data.get('category') or "Measuring Tools"
            shopify_product.status = "active" if product_data.get('availability', '').lower() == 'in stock' else "draft"
            
            # Variant bilgilerini ekleyelim
            variant = shopify.Variant()
            variant.sku = product_data['sku']
            variant.price = str(product_data.get('price', 0.00))
            if product_data.get('original_price'):
                variant.compare_at_price = str(product_data['original_price'])
            variant.inventory_management = "shopify"
            variant.inventory_quantity = 100 if product_data.get('availability', '').lower() == 'in stock' else 0
            variant.option1 = "Default Title"  # Tek variant için gerekli
            
            shopify_product.variants = [variant]
            
            # Resim varsa ekleyelim
            if product_data.get('image_url'):
                image = shopify.Image()
                image.src = product_data['image_url']
                shopify_product.images = [image]
            
            # Ürünü kaydedelim
            if not shopify_product.save():
                logger.error(f"Failed to create product for SKU {product_data['sku']}")
                return False
            
            # Metafield'ları ayrı ayrı kaydedelim
            metafields = {
                'range': product_data.get('range', ''),
                'reading': product_data.get('reading', ''),
                'family': product_data.get('family', ''),
                'weight': product_data.get('weight', ''),
                'dimensions': product_data.get('dimensions', '')
            }
            
            for key, value in metafields.items():
                if value:
                    try:
                        metafield = shopify.Metafield({
                            'namespace': 'custom',
                            'key': key,
                            'value': str(value),
                            'type': 'single_line_text_field',
                            'owner_id': shopify_product.id,
                            'owner_resource': 'product'
                        })
                        metafield.save()
                    except Exception as e:
                        logger.warning(f"Failed to set metafield {key} for product {shopify_product.id}: {str(e)}")
                        continue
            
            logger.info(f"Successfully created product with SKU {product_data['sku']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating product {product_data['sku']}: {str(e)}")
            return False

    def _update_product(self, existing_product: shopify.Product, existing_variant: shopify.Variant, product_data: Dict[str, Any]) -> bool:
        """Update an existing product in Shopify using GraphQL"""
        try:
            mutation = """
            mutation productUpdate($input: ProductInput!) {
                productUpdate(input: $input) {
                    product {
                        id
                        variants(first: 1) {
                            edges {
                                node {
                                    id
                                }
                            }
                        }
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
            """
            
            variables = {
                'input': {
                    'id': f"gid://shopify/Product/{existing_product.id}",
                    'title': product_data['title'] or f"INSIZE {product_data['sku']}",
                    'descriptionHtml': product_data['description'],
                    'vendor': "INSIZE",
                    'productType': product_data['category'] or "Measuring Tools",
                    'status': "ACTIVE" if product_data['availability'].lower() == 'in stock' else "DRAFT",
                    'variants': [{
                        'id': f"gid://shopify/ProductVariant/{existing_variant.id}",
                        'sku': product_data['sku'],
                        'price': str(product_data['price']) if product_data['price'] else "0.00",
                        'compareAtPrice': str(product_data['original_price']) if product_data['original_price'] else None,
                        'inventoryQuantities': [{
                            'availableQuantity': 100 if product_data['availability'].lower() == 'in stock' else 0
                        }]
                    }]
                }
            }
            
            if product_data.get('image_url') and not existing_product.images:
                variables['input']['images'] = [{'src': product_data['image_url']}]
            
            response = requests.post(
                self.graphql_url,
                json={'query': mutation, 'variables': variables},
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"GraphQL mutation failed for SKU {product_data['sku']}: {response.text}")
                return False
            
            data = response.json()
            user_errors = data.get('data', {}).get('productUpdate', {}).get('userErrors', [])
            
            if user_errors:
                logger.error(f"Failed to update product for SKU {product_data['sku']}: {user_errors}")
                return False
            
            # Update metafields
            self._set_metafields(existing_product.id, product_data)
            
            logger.info(f"Successfully updated product with SKU {product_data['sku']}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating product {product_data['sku']}: {str(e)}")
            return False

    def _set_metafields(self, product_id: int, product_data: Dict[str, Any]) -> None:
        """Set metafields for a product"""
        metafields = {
            'range': product_data.get('range', ''),
            'reading': product_data.get('reading', ''),
            'family': product_data.get('family', ''),
            'weight': product_data.get('weight', ''),
            'dimensions': product_data.get('dimensions', '')
        }
        
        for key, value in metafields.items():
            if value:
                try:
                    metafield = shopify.Metafield({
                        'namespace': 'custom',
                        'key': key,
                        'value': str(value),
                        'type': 'single_line_text_field',
                        'owner_id': product_id,
                        'owner_resource': 'product'
                    })
                    metafield.save()
                except Exception as e:
                    logger.warning(f"Failed to set metafield {key} for product {product_id}: {str(e)}")

    def _find_product_by_sku(self, sku: str) -> tuple:
        """Find a product and its variant by SKU using GraphQL"""
        try:
            query = """
            query($query: String!) {
                products(first: 1, query: $query) {
                    edges {
                        node {
                            id
                            title
                            variants(first: 1) {
                                edges {
                                    node {
                                        id
                                        sku
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            
            variables = {
                'query': f'variant:sku:"{sku}"'
            }
            
            response = requests.post(
                self.graphql_url,
                json={'query': query, 'variables': variables},
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"GraphQL query failed for SKU {sku}: {response.text}")
                return None, None
            
            data = response.json()
            products = data.get('data', {}).get('products', {}).get('edges', [])
            
            if not products:
                logger.info(f"No existing product found for SKU {sku}")
                return None, None
            
            product_data = products[0]['node']
            product_id = product_data['id'].split('/')[-1]  # Extract numeric ID
            variant_data = product_data['variants']['edges'][0]['node']
            variant_id = variant_data['id'].split('/')[-1]  # Extract numeric ID
            
            # Get full product and variant objects
            product = shopify.Product.find(product_id)
            variant = shopify.Variant.find(variant_id)
            
            logger.info(f"Found existing product with SKU {sku}")
            return product, variant
            
        except Exception as e:
            logger.error(f"Error finding product for SKU {sku}: {str(e)}")
            return None, None

    def sync_products(self, is_initial_load: bool = False):
        """Sync products to Shopify"""
        try:
            db = Database()
            db.connect()
            
            # Get products from database
            if is_initial_load:
                logger.info("Starting initial bulk load of all products...")
                products_df = db.get_all_products()
            else:
                # Get only products modified since last sync
                last_sync = db.get_last_successful_sync()
                if last_sync:
                    logger.info(f"Getting products modified since {last_sync}")
                    products_df = db.get_modified_products(last_sync)
                else:
                    logger.info("No previous successful sync found, getting all products...")
                    products_df = db.get_all_products()
            
            products = products_df.to_dict('records')
            total_products = len(products)
            
            if total_products == 0:
                logger.info("No products to sync")
                db.log_sync(
                    products_updated=0,
                    products_added=0,
                    status="SUCCESS",
                    error_message=""
                )
                return
            
            logger.info(f"Starting sync of {total_products} products...")
            
            # Process products in batches
            batch_size = 1000 if is_initial_load else 50
            success_count = 0
            error_count = 0
            
            for i in range(0, total_products, batch_size):
                batch = products[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} products)...")
                
                for product_data in batch:
                    # Find existing product
                    existing_product, existing_variant = self._find_product_by_sku(product_data['sku'])
                    
                    # Create or update product
                    if existing_product and existing_variant:
                        success = self._update_product(existing_product, existing_variant, product_data)
                    else:
                        success = self._create_product(product_data)
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # Add small delay to avoid rate limits
                    time.sleep(0.5)
                
                logger.info(f"Batch {i//batch_size + 1} complete. Progress: {success_count + error_count}/{total_products}")
            
            status = "SUCCESS" if error_count == 0 else "PARTIAL_SUCCESS"
            error_message = f"{error_count} products failed to sync" if error_count > 0 else ""
            
            logger.success(f"Completed Shopify sync. Successfully synced {success_count}/{total_products} products")
            
            # Log sync in database
            db.log_sync(
                products_updated=success_count,
                products_added=success_count,
                status=status,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Shopify sync failed: {str(e)}")
            if 'db' in locals():
                db.log_sync(
                    products_updated=0,
                    products_added=0,
                    status="FAILED",
                    error_message=str(e)
                )
            raise
        finally:
            if 'db' in locals():
                db.close() 