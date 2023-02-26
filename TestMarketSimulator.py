import unittest
from chapter7.LiquidityProvider import LiquidityProvider
from chapter7.TradingStrategy import TradingStrategy

class TestMarketSimulator(unittest.TestCase):
    def setUp(self):
        self.liquidity_provider = LiquidityProvider()
        self.trading_strategy = TradingStrategy()
    
    def test_add_liquidity(self):
        self.liquidity_provider.generate_random_order()
        self.assertEqual(self.liquidity_provider.orders[0]['id'], 0)
        self.assertEqual(self.liquidity_provider.orders[0]['side'], 'buy')
        self.assertEqual(self.liquidity_provider.orders[0]['quantity'], 700)
        self.assertEqual(self.liquidity_provider.orders[0]['price'], 11)

    def test_receive_top_of_book(self):
        book_event = {
            'bid_price': 12,
            'bid_quantity': 100,
            'offer_price': 11,
            'offer_quantity': 150
        }

        self.trading_strategy.handle_book_event(book_event=book_event)
        self.assertEqual(len(self.trading_strategy.orders), 2)
        self.assertEqual(self.trading_strategy.orders[0]['side'], 'sell')
        self.assertEqual(self.trading_strategy.orders[1]['side'], 'buy')