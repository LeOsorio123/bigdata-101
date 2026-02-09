"""
Sales Analytics - Business intelligence with MapReduce.

Analyzes sales data to generate business insights:
- Total revenue by product
- Sales by category
- Top-selling products
- Regional performance

Input format (JSON per line):
{"product_id": "P001", "product": "Laptop", "category": "Electronics", 
 "amount": 1200, "quantity": 1, "region": "North", "date": "2026-01-15"}

Usage:
    python mr_sales_analytics.py sales_data.json
    python mr_sales_analytics.py --metric=product sales_data.json
    python mr_sales_analytics.py --metric=category sales_data.json
    python mr_sales_analytics.py --metric=region sales_data.json
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol
import json


class MRSalesAnalytics(MRJob):
    """
    Analyze sales data for business insights.
    
    Input: JSON lines with sales transactions
    Output: Analytics based on selected metric
    """
    
    OUTPUT_PROTOCOL = JSONValueProtocol
    
    def configure_args(self):
        """Add custom command-line arguments."""
        super(MRSalesAnalytics, self).configure_args()
        self.add_passthru_arg(
            '--metric',
            default='product',
            choices=['product', 'category', 'region', 'top'],
            help='Metric to analyze'
        )
        self.add_passthru_arg(
            '--top-n',
            type=int,
            default=10,
            help='Number of top items to show (for top metric)'
        )
    
    def steps(self):
        """Define job steps."""
        if self.options.metric == 'top':
            # Top products need sorting step
            return [
                MRStep(mapper=self.mapper_sales,
                       combiner=self.combiner_sum,
                       reducer=self.reducer_sum),
                MRStep(reducer=self.reducer_top_products)
            ]
        else:
            # Simple aggregation
            return [
                MRStep(mapper=self.mapper_sales,
                       combiner=self.combiner_sum,
                       reducer=self.reducer_analytics)
            ]
    
    # ===== STEP 1: Parse and aggregate =====
    
    def mapper_sales(self, _, line):
        """
        Parse sales data and emit based on metric.
        
        Args:
            _: Key (ignored)
            line: JSON line with sales data
        
        Yields:
            (key, amount) based on selected metric
        """
        try:
            sale = json.loads(line)
            
            metric = self.options.metric
            amount = sale.get('amount', 0)
            
            if metric == 'product' or metric == 'top':
                key = sale.get('product', 'Unknown')
            elif metric == 'category':
                key = sale.get('category', 'Unknown')
            elif metric == 'region':
                key = sale.get('region', 'Unknown')
            else:
                return
            
            yield (key, amount)
            
        except (json.JSONDecodeError, KeyError):
            # Skip malformed data
            pass
    
    def combiner_sum(self, key, amounts):
        """
        Partial sum on mapper nodes.
        
        Args:
            key: Product/category/region
            amounts: Iterator of amounts
        
        Yields:
            (key, partial_sum)
        """
        yield (key, sum(amounts))
    
    def reducer_sum(self, key, amounts):
        """
        Sum all amounts for each key (for top products).
        
        Args:
            key: Product/category/region
            amounts: Iterator of amounts
        
        Yields:
            (None, (total, key)) for sorting
        """
        total = sum(amounts)
        # For top products, emit to same reducer
        yield None, (total, key)
    
    def reducer_analytics(self, key, amounts):
        """
        Calculate analytics for each key.
        
        Args:
            key: Product/category/region
            amounts: Iterator of amounts
        
        Yields:
            (key, analytics_dict)
        """
        amounts_list = list(amounts)
        
        analytics = {
            'total_revenue': sum(amounts_list),
            'transactions': len(amounts_list),
            'avg_transaction': round(sum(amounts_list) / len(amounts_list), 2)
        }
        
        yield (key, analytics)
    
    # ===== STEP 2: Find top products =====
    
    def reducer_top_products(self, _, product_revenues):
        """
        Find top N products by revenue.
        
        Args:
            _: Key (None)
            product_revenues: Iterator of (revenue, product) tuples
        
        Yields:
            (rank, product_info)
        """
        # Sort by revenue (descending) and take top N
        top_products = sorted(product_revenues, reverse=True)[:self.options.top_n]
        
        for rank, (revenue, product) in enumerate(top_products, 1):
            yield (rank, {
                'product': product,
                'revenue': revenue
            })


if __name__ == '__main__':
    MRSalesAnalytics.run()
