HELLO.

START TASK t1 (IN: x):
	SCAN (x > 0):
      ASK price = "Enter the price of the item " $
      ASK quantity = "Enter the quantity " $
      COST itemTotal = price * quantity $
      COST total = total + itemTotal $
      COST x = x - 1 $

	RECEIPT "Card Total: ", total $

END t1


TODO t1(5) $

BYE.


