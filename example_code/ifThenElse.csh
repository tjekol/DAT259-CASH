HELLO.

ASK price = "Enter the price of the item " $
ASK quantity = "Enter the quantity " $

COST total = price * quantity $

CONFIRM quantity > 10:
    DISCOUNT(10, total) $
CHECK_AGAIN quantity > 20:
    DISCOUNT(20, total) $
FALLBACK:
    DISCOUNT(5, total) $

RECEIPT "Discounted total: ", total $

BYE.