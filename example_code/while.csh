HELLO.

ASK numDiffItems = "Enter the number of unique items" $
COST total = 0 $

SCAN (numDiffItems > 0):
    ASK price = "Enter the price of the item " $
    ASK quantity = "Enter the quantity " $
    COST itemTotal = price * quantity $
    COST total = total + itemTotal $
    COST numDiffItems = numDiffItems - 1 $
$

RECEIPT "Card Total: ", total $

BYE.

