from collections import deque
from typing import Tuple, Dict, List


class TradingStrategy:
    def __init__(self, ob_2_ts, ts_2_om, om_2_ts):
        self.orders: List[Dict] = []
        self.order_id: int = 0
        self.position: int = 0
        self.pnl: float = 0.0
        self.cash: float = 10000.0
        self.current_bid = 0
        self.current_offer = 0
        self.ob_2_ts: deque = ob_2_ts
        self.ts_2_om = ts_2_om
        self.om_2_ts = om_2_ts

    def handle_input_from_bb(self, book_event: Dict = None):
        if self.ob_2_ts is None:
            print('simulation mode')
            self.handle_book_event(book_event=book_event)
        else:
            if len(self.ob_2_ts) > 0:
                be = self.ob_2_ts.popleft()
                self.handle_book_event(book_event=be)
    
    def handle_book_event(self, book_event: Dict):
        if book_event is not None:
            self.current_bid = book_event['bid_price']
            self.current_offer = book_event['offer_price']
        
        if self.signal(book_event=book_event):
            self.create_orders(book_event, min(book_event['bid_quantity'], book_event['offer_quantity']))
        
        self.execution()
    
    def signal(self, book_event: Dict) -> bool:
        if book_event is not None:
            if book_event['bid_price'] > book_event['ask_price']:
                if book_event['bid_price'] > 0 and book_event['offer_price'] > 0:
                    return True
                else:
                    return False
        else:
            return False
    
    def create_orders(self, book_event: Dict, quantity: int) -> None:
        self.order_id += 1
        order = {
            'id': self.order_id,
            'price': book_event['bid_price'],
            'quantity': quantity,
            'side': 'sell',
            'action': 'to_be_sent'
        }
        self.orders.append(order.copy())

        self.order_id += 1
        order = {
            'id': self.order_id,
            'price': book_event['offer_price'],
            'quantity': quantity,
            'side': 'buy',
            'action': 'to_be_sent'
        }

        self.orders.append(order.copy())
    
    def execution(self):
        orders_to_be_removed = []
        for index, order in enumerate(self.orders):
            if order['action'] == 'to_be_sent':
                # Send order
                order['status'] = 'new'
                order['action'] = 'no_action'
                if self.ts_2_om is None:
                    print('simulation_mode')
                else:
                    self.ts_2_om.append(order.copy())
            
            if order['status'] == 'rejected':
                orders_to_be_removed.append(index)
            if order['status'] == 'filled':
                orders_to_be_removed.append(index)
                pos = order['quantity'] if order['side'] == 'buy' else -order['quantity']
                self.position += pos
                self.pnl -= pos*order['price']
                self.cash -= pos*order['price']
        
        for order_index in sorted(orders_to_be_removed, reverse=True):
            del (self.orders[order_index])

    def handle_response_from_om(self):
        if self.om_2_ts is not None:
            self.handle_market_response(self.om_2_ts.popleft())
        else:
            print('simulation mode')
    
    def handle_market_response(self, order_execution: Dict):
        order, _ = self.lookup_orders(order_execution['id'])
        if order is None:
            print('error not found')
            return
        order['status']  = order_execution['status']

        self.execution()
    
    def lookup_orders(self, id) -> Tuple[Dict, int]:
        count=0
        for o in self.orders:
            if o['id'] == id:
                return o, count
            count += 1
        
        return None, None
