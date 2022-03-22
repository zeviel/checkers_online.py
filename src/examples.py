# Simple login that uses authorization token
import checkersonline
checlient = checkersonline.CheckersClient(token="")
print(f"-- Account user_id is::: {checlient.user_id}")
