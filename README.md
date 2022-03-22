# checkersonline.py
- API For [CheckersOnline](https://play.google.com/store/apps/details?id=com.rstgames.checkers)
- Библиотека для [Шашки Онлайн](https://play.google.com/store/apps/details?id=com.rstgames.checkers)

## Example
```py3
# Simple login that uses authorization token
import checkersonline
checlient = checkersonline.CheckersClient(token="")
print(f"-- Account user_id is::: {checlient.user_id}")
```
