#!/bin/bash

# The files in html are copied from live session used for testing without having to create a login session. 
# This script is used to remove any personal data.

total_replacements=0

for file in tests/html/*.html; do
  # Count what will be replaced
  count1=$(grep -o '"firstName":"[^"]*"' "$file" 2>/dev/null | wc -l)
  count2=$(grep -o '"lastName":"[^"]*"' "$file" 2>/dev/null | wc -l)
  count3=$(grep -o '"customerGUID":"[^"]*"' "$file" 2>/dev/null | wc -l)
  count4=$(grep -o '"rememberMeId":"[^"]*"' "$file" 2>/dev/null | wc -l)
  # Match text inside the span that follows the WelcomeButton account icon
  count5=$(grep -o 'Welcome-button--desktopV2[^>]*>.*citrus-Text--m">[^<]*</span>' "$file" 2>/dev/null | wc -l)
  total_replacements=$((total_replacements + count1 + count2 + count3 + count4 + count5))

  sed -i 's/"firstName":"[^"]*"/"firstName":"TestUsername"/g' "$file"
  sed -i 's/"lastName":"[^"]*"/"lastName":"TestLastname"/g' "$file"
  sed -i 's/"customerGUID":"[^"]*"/"customerGUID":"0b1234g5-6d7b-4567-a123-er7b78gd6789"/g' "$file"
  sed -i 's/"rememberMeId":"[^"]*"/"rememberMeId":"TestUsername.TesLastname@gmail.com"/g' "$file"
  # Structural replacement for the user name in the header
  sed -i 's/\(Welcome-button--desktopV2[^>]*>.*citrus-Text--m">\)[^<]*\(<\/span>\)/\1User\2/g' "$file"
done

echo "Test data anonymized. Made $total_replacements replacement(s)."
