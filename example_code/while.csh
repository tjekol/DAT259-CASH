HELLO.

ASK numDiffItems = "Enter the price of the item " $

SCAN (numDiffItems > 0):
    ASK price = "Enter the price of the item " $
    ASK quantity = "Enter the quantity " $
    COST itemTotal = price * quantity $
    COST total = total + itemTotal $
    COST numDiffItems = numDiffItems - 1 $

RECEIPT "Card Total: ", total $

BYE.