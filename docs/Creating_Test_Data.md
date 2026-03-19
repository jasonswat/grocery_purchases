# Adding webpages for test data

The website can change often as developers add more features. You may need to download the mypurchases page and a recept page to test and make sure it still works as expected.

1. Go to https://www.qfc.com/mypurchases
That page should show your most recent purchases. Right click and "Save Page As" then chose "Webpage Complete", chose the location under the html directory and save it with a new name.
2. Go to a receipt and save one of the receipt pages (something with a variety of items), "Save Page As" then "Webpage Complete" and save as receipt(number).html
3. Update [../../src/util/helper_get_receipts.py](helper_get_receipts.py) the 3 variables and point to the new saved files:
```
purchases_url = f"file://{project_root}/tests/html/mypurchases.html"
receipt_url = f"file://{project_root}/tests/html/Receipt4.html"
test_receipt_id = "705~00851~2025-12-05~10~2121723"
```
4. Edit the html pages and remove or comment out most of the java script at the top, something like this:
```html
  <script> ...</script> 
<!-- 
<script ... 
<script ... 
<script ...
<script ...
<script ...
<script ...
<script ...
<script ... 
<script ... 
-->
```
4. Run `make test_get_receipts` to test, fix what breaks

