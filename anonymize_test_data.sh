#!/bin/bash

# The files in html are copied from live session used for testing without having to create a login session. 
# This script is used to remove any personal data.

for file in tests/html/*.html; do
  sed -i 's/"firstName":"[^"]*"/"firstName":"TestUsername"/g' "$file"
  sed -i 's/"lastName":"[^"]*"/"lastName":"TestLastname"/g' "$file"
  sed -i 's/"customerGUID":"[^"]*"/"customerGUID":"0b1234g5-6d7b-4567-a123-er7b78gd6789"/g' "$file"
  sed -i 's/"rememberMeId":"[^"]*"/"rememberMeId":"TestUsername.TesLastname@gmail.com"/g' "$file"
done

echo "Test data anonymized."
