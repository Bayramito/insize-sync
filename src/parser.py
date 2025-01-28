import pandas as pd
from loguru import logger
from typing import Dict, List, Optional

class ExcelParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def parse(self) -> List[Dict]:
        """Parse the Excel file and return a list of product dictionaries"""
        try:
            logger.info(f"Reading Excel file: {self.file_path}")
            df = pd.read_excel(self.file_path)
            
            # Skip the first row as it contains column headers
            products = []
            for index, row in df.iloc[1:].iterrows():
                try:
                    product = self._transform_row(row)
                    if product and self._validate_product(product):
                        products.append(product)
                except Exception as e:
                    logger.error(f"Failed to transform row: {str(e)}")
                    continue
                    
            logger.info(f"Successfully parsed {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Failed to parse Excel file: {str(e)}")
            return []
            
    def _transform_row(self, row: pd.Series) -> Optional[Dict]:
        """Transform a row into a product dictionary"""
        try:
            # Extract values with proper error handling
            sku = str(row['Unnamed: 1']).strip() if pd.notna(row['Unnamed: 1']) else None
            if not sku or sku == 'No':  # Skip header row or empty SKU
                return None
                
            description = str(row['Unnamed: 2']).strip() if pd.notna(row['Unnamed: 2']) else ''
            description2 = str(row['Unnamed: 3']).strip() if pd.notna(row['Unnamed: 3']) else ''
            
            # Combine descriptions for title
            title = description
            if description2:
                title = f"{description} - {description2}"
                
            # Handle availability - keep as string
            availability = str(row['Unnamed: 4']).strip() if pd.notna(row['Unnamed: 4']) else '0'
            if availability == 'Availability':  # Skip header row
                return None
                
            # Handle price and discount
            try:
                price = float(row['Unnamed: 16']) if pd.notna(row['Unnamed: 16']) else 0.0
                if isinstance(price, str) and price == 'Precio':  # Skip header row
                    return None
            except (ValueError, TypeError):
                price = 0.0
                
            try:
                discount = float(row['Unnamed: 17']) if pd.notna(row['Unnamed: 17']) else 0.0
                if isinstance(discount, str) and discount == 'Descuento EU':  # Skip header row
                    return None
            except (ValueError, TypeError):
                discount = 0.0
                
            # Apply discount if available
            original_price = price
            if discount > 0:
                price = price * (1 - discount/100)
                
            # Build product dictionary
            product = {
                'sku': sku,
                'title': title,
                'description': description,
                'description2': description2,
                'availability': availability,
                'price': price,
                'original_price': original_price,
                'discount': discount,
                'range': str(row['Unnamed: 5']).strip() if pd.notna(row['Unnamed: 5']) else '',
                'reading': str(row['Unnamed: 6']).strip() if pd.notna(row['Unnamed: 6']) else '',
                'family': str(row['Unnamed: 7']).strip() if pd.notna(row['Unnamed: 7']) else '',
                'weight': str(row['Unnamed: 8']).strip() if pd.notna(row['Unnamed: 8']) else '',
                'dimensions': str(row['Unnamed: 9']).strip() if pd.notna(row['Unnamed: 9']) else '',
                'image_url': str(row['Unnamed: 10']).strip() if pd.notna(row['Unnamed: 10']) else '',
                'product_url': str(row['Unnamed: 11']).strip() if pd.notna(row['Unnamed: 11']) else '',
                'category': str(row['Unnamed: 12']).strip() if pd.notna(row['Unnamed: 12']) else '',
                'subcategory': str(row['Unnamed: 13']).strip() if pd.notna(row['Unnamed: 13']) else '',
            }
            
            return product
            
        except Exception as e:
            logger.error(f"Failed to transform row: {str(e)}")
            return None
            
    def _validate_product(self, product: Dict) -> bool:
        """Validate product data"""
        try:
            # Check required fields
            required_fields = ['sku']  # Only SKU is required
            for field in required_fields:
                if not product.get(field):
                    logger.warning(f"Product missing required field: {field}")
                    return False
                    
            # Log missing optional fields
            optional_fields = ['title', 'price']
            for field in optional_fields:
                if not product.get(field):
                    logger.warning(f"Product missing optional field: {field}")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate product: {str(e)}")
            return False 