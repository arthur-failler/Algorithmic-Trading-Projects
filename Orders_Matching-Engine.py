import time

from enum import Enum
class OrderType(Enum):
    LIMIT = 1
    MARKET = 2
    IOC = 3

class OrderSide(Enum):
    BUY = 1
    SELL = 2


class NonPositiveQuantity(Exception):
    pass

class NonPositivePrice(Exception):
    pass

class InvalidSide(Exception):
    pass

class UndefinedOrderType(Exception):
    pass

class UndefinedOrderSide(Exception):
    pass

class NewQuantityNotSmaller(Exception):
    pass

class UndefinedTraderAction(Exception):
    pass

class UndefinedResponse(Exception):
    pass


from abc import ABC


class Order(ABC):
    def __init__(self, id, symbol, quantity, side, time):
        self.id = id
        self.symbol = symbol
        if quantity > 0:
            self.quantity = quantity
        else:
            raise NonPositiveQuantity("Quantity Must Be Positive!")
        if side in [OrderSide.BUY, OrderSide.SELL]:
            self.side = side
        else:
            raise InvalidSide("Side Must Be Either \"Buy\" or \"OrderSide.SELL\"!")
        self.time = time


class LimitOrder(Order):
    def __init__(self, id, symbol, quantity, price, side, time):
        super().__init__(id, symbol, quantity, side, time)
        if price > 0:
            self.price = price
        else:
            raise NonPositivePrice("Price Must Be Positive!")
        self.type = OrderType.LIMIT


class MarketOrder(Order):
    def __init__(self, id, symbol, quantity, side, time):
        super().__init__(id, symbol, quantity, side, time)
        self.type = OrderType.MARKET


class IOCOrder(Order):
    def __init__(self, id, symbol, quantity, price, side, time):
        super().__init__(id, symbol, quantity, side, time)
        if price > 0:
            self.price = price
        else:
            raise NonPositivePrice("Price Must Be Positive!")
        self.type = OrderType.IOC
    

class FilledOrder(Order):
    def __init__(self, id, symbol, quantity, price, side, time, limit = False):
        super().__init__(id, symbol, quantity, side, time)
        self.price = price
        self.limit = limit
        


class MatchingEngine():
    def __init__(self):
        self.bid_book = []
        self.ask_book = []


    def handle_order(self, order):
        # Call different functions from the matching engine depending on the type of given order
        
        try:
            if order.type == OrderType.LIMIT:
                return self.handle_limit_order(order)
                
            if order.type == OrderType.MARKET:
                return self.handle_limit_order(order)
                
            if order.type == OrderType.IOC:
                return self.handle_limit_order(order)
        except:
            raise UndefinedOrderType("Undefined Order Type!")

    
    def handle_limit_order(self, order):
        #Accepts an arbitrary limit order that can either be filled if the limit order price crosses the book,
        #or placed in the book.
        # The filled orders are placed into the below list
        filled_orders = []
        
        try:
            q = order.quantity

            # If order is a BUY  
            if order.side == OrderSide.BUY:
                
                if self.ask_book == []:
                    self.insert_limit_order(order)
                    return filled_orders
                
                for i in range(len(self.ask_book)):
                    
                    if self.ask_book[i].price <= order.price:
                        
                        if self.ask_book[i].quantity <= q:
                            
                            filled_orders.append(self.ask_book[i])
                            q -= self.ask_book[i].quantity

                        elif self.ask_book[i].quantity > order.quantity:
                            
                            self.ask_book[i].quantity -= q
                            filled_orders.append(order)
                            return filled_orders
                        
                    else:
                        
                        order.quantity = q
                        self.insert_limit_order(order)
                        return filled_orders
                        
            # If order is a SELL
            elif order.side == OrderSide.SELL:
                
                if self.bid_book == []:
                    self.insert_limit_order(order)
                    return filled_orders
                
                for i in range(len(self.bid_book)):
                    
                    if self.bid_book[i].price >= order.price:
                        
                        if self.bid_book[i].quantity <= q:
                            
                            filled_orders.append(self.bid_book[i])
                            q -= self.bid_book[i].quantity

                        elif self.bid_book[i].quantity > q:
                            
                            o = self.bid_book[i]
                            self.bid_book[i].quantity -= q
                            self.bid_book = [e for e in self.bid_book if e not in filled_orders] 
                            filled_orders.append(order)
                            filled_orders.append(o)
                            return filled_orders
                            
                    else:
                    
                        order.quantity = q
                        self.insert_limit_order(order)
                        self.bid_book = [e for e in self.bid_book if e not in filled_orders] 
                        return filled_orders
                                            
            return filled_orders
        
        # Raise ERROR if neither BUY or SELL
        except:
            print('ERROR')
            raise UndefinedOrderSide("Undefined Order Side!")


    def handle_market_order(self, order):
        #Handles an arbitrary market order.
        # The filled orders are placed into the below list
        filled_orders = []
        
        try:
            
            q = order.quantity
                      
            if order.side == OrderSide.BUY:
                
                if self.ask_book == []:
                    return filled_orders
                
                for i in range(len(self.ask_book)):
                    
                        
                    if self.ask_book[i].quantity <= q:
                        
                        filled_orders.append(self.ask_book[i])
                        q -= self.ask_book[i].quantity

                    elif self.ask_book[i].quantity > order.quantity:
                        
                        o = self.ask_book[i]
                        self.ask_book[i].quantity -= q
                        self.ask_book = [e for e in self.ask_book if e not in filled_orders] 
                        filled_orders.append(o)
                        return filled_orders
                        
                return filled_orders
            
                    
            elif order.side == OrderSide.SELL:
                
                if self.bid_book == []:
                    self.insert_limit_order(order)
                    return filled_orders
                
                for i in range(len(self.bid_book)):

                    if self.bid_book[i].quantity <= q:

                        filled_orders.append(self.bid_book[i])
                        q -= self.bid_book[i].quantity

                    elif self.bid_book[i].quantity > q:

                        o = self.bid_book[i]
                        self.bid_book[i].quantity -= q
                        self.bid_book = [e for e in self.bid_book if e not in filled_orders] 
                        filled_orders.append(o)
                        return filled_orders

                return filled_orders
                        
            return filled_orders
            
        except:
            # You need to raise the following error if the side the order is for is ambiguous
            raise UndefinedOrderSide("Undefined Order Side!")
            

    def handle_ioc_order(self, order):
        #Handles an arbitrary IOC order.
        # The filled orders are placed into the below list.
        filled_orders = []
        
        return filled_orders
        
        raise UndefinedOrderSide("Undefined Order Side!")


    def insert_limit_order(self, order):
        assert order.type == OrderType.LIMIT
        #Place limit orders in the book that are guaranteed to not immediately fill
        try:
            if order.side == OrderSide.BUY:
                self.bid_book.append(order)
            if order.side == OrderSide.SELL:
                self.bid_book.append(order)
                
            self.bid_book = sorted(self.bid_book, key=lambda x: -x.price)
            self.ask_book = sorted(self.ask_book, key=lambda x: x.price)

        # Raise ERROR if not BUY or SELL
        except:
            raise UndefinedOrderSide("Undefined Order Side!")
