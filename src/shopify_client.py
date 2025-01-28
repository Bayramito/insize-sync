import shopify
from loguru import logger
from typing import List, Dict, Any
from . import config

class ShopifyClient:
    def __init__(self):
        self.setup_shopify()
        
    def setup_shopify(self):
        """Initialize Shopify API connection"""
        try:
            shop_url = f"https://{config.SHOPIFY_ACCESS_TOKEN}@{config.SHOPIFY_SHOP_URL}/admin/api/2024-01"
            shopify.ShopifyResource.set_site(shop_url)
            logger.info("Shopify API connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Shopify API: {str(e)}")
            raise
            
    def update_products(self, products: List[Dict[str, Any]]) -> tuple:
        """Update or create products in Shopify
        Returns tuple of (updated_count, added_count)
        """
        updated = 0
        added = 0
        
        try:
            for product_data in products:
                try:
                    # Try to find existing product by SKU
                    existing_products = shopify.Product.find(
                        sku=product_data['sku']
                    )
                    
                    if existing_products:
                        self._update_product(existing_products[0], product_data)
                        updated += 1
                    else:
                        self._create_product(product_data)
                        added += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process product {product_data.get('sku')}: {str(e)}")
                    continue
                    
            logger.info(f"Successfully processed {updated} updates and {added} additions")
            return updated, added
            
        except Exception as e:
            logger.error(f"Failed to update products: {str(e)}")
            raise
            
    def _create_product(self, product_data: Dict[str, Any]):
        """Create new product in Shopify"""
        try:
            new_product = shopify.Product()
            new_product.title = product_data['title']
            new_product.body_html = product_data.get('description', '')
            
            # Create variant
            variant = shopify.Variant({
                'price': str(product_data['price']),
                'sku': product_data['sku'],
                'inventory_management': 'shopify',
                'inventory_quantity': product_data['stock']
            })
            
            new_product.variants = [variant]
            new_product.save()
            
            # Set inventory
            self._update_inventory(variant, product_data['stock'])
            
            logger.info(f"Created new product: {product_data['sku']}")
            
        except Exception as e:
            logger.error(f"Failed to create product {product_data.get('sku')}: {str(e)}")
            raise
            
    def _update_product(self, product: shopify.Product, product_data: Dict[str, Any]):
        """Update existing product in Shopify"""
        try:
            product.title = product_data['title']
            product.body_html = product_data.get('description', '')
            
            # Update variant
            variant = product.variants[0]
            variant.price = str(product_data['price'])
            
            product.save()
            
            # Update inventory
            self._update_inventory(variant, product_data['stock'])
            
            logger.info(f"Updated product: {product_data['sku']}")
            
        except Exception as e:
            logger.error(f"Failed to update product {product_data.get('sku')}: {str(e)}")
            raise
            
    def _update_inventory(self, variant: shopify.Variant, quantity: int):
        """Update product inventory"""
        try:
            location = self._get_default_location()
            
            inventory_item = shopify.InventoryItem.find(
                variant.inventory_item_id
            )
            
            inventory_level = shopify.InventoryLevel.find(
                inventory_item_id=variant.inventory_item_id,
                location_id=location.id
            )
            
            if inventory_level:
                inventory_level.set(quantity)
            else:
                shopify.InventoryLevel.connect(
                    location.id,
                    variant.inventory_item_id
                )
                shopify.InventoryLevel.set(
                    location.id,
                    variant.inventory_item_id,
                    quantity
                )
                
        except Exception as e:
            logger.error(f"Failed to update inventory: {str(e)}")
            raise
            
    def _get_default_location(self) -> shopify.Location:
        """Get default inventory location"""
        try:
            locations = shopify.Location.find()
            if not locations:
                raise Exception("No locations found")
            return locations[0]
        except Exception as e:
            logger.error(f"Failed to get default location: {str(e)}")
            raise 