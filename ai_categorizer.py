# import json
# from collections import Counter
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.model_selection import train_test_split
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.svm import LinearSVC

# with open("CATEGORY_MAP.json", "r") as f:
#     data = json.load(f)
    
    
#     merchant_names = []
#     categories = []

#     for key, value in data.items():
#         # print(key, value['category'])
#         merchant_names.append(key)
#         categories.append(value['category'])

#     for i in range(0, 5):
#         # print(merchant_names[i], categories[i])
#         pass


#     # print(Counter(categories).most_common())
#     # print(len(merchant_names))


# vectorizer = TfidfVectorizer()

# X = vectorizer.fit_transform(merchant_names)
# print(X.shape)
# print(vectorizer.get_feature_names_out()[:10])

# X_train, X_test, Y_train, Y_test = train_test_split(X, categories, test_size=0.2, random_state=42)
# model = MultinomialNB()

# model.fit(X_train, Y_train)

# print("Train Size:",X_train.shape)
# print("Test Size:", X_test.shape)
# print("Accuracy:", model.score(X_test,Y_test))

# y_pred = model.predict(X_test)

# for i in range(min(10, len(Y_test))):
#     actual = Y_test[i]
#     predicted = y_pred[i]
#     status = "✅" if actual == predicted else "❌"
#     print(f"{status} Actual: {actual:25s} | Predicted: {predicted}")

# model2 = LinearSVC(class_weight="balanced", random_state=42)
# model2.fit(X_train, Y_train)

# print("\n--- SVM Results ---")
# print("Accuracy:", model2.score(X_test, Y_test))

# y_pred2 = model2.predict(X_test)
# for i in range(min(10, len(Y_test))):
#     actual = Y_test[i]
#     predicted = y_pred2[i]
#     status = "✅" if actual == predicted else "❌"
#     print(f"{status} Actual: {actual:25s} | Predicted: {predicted}")

# vectorizer2 = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
# X2 = vectorizer2.fit_transform(merchant_names)

# X2_train, X2_test, y2_train, y2_test = train_test_split(
#     X2, categories, test_size=0.2, random_state=42
# )

# model3 = LinearSVC(class_weight='balanced', random_state=42)
# model3.fit(X2_train, y2_train)

# print("\n--- SVM + Char N-grams ---")
# print("Accuracy:", model3.score(X2_test, y2_test))

# y_pred3 = model3.predict(X2_test)
# for i in range(min(10, len(y2_test))):
#     actual = y2_test[i]
#     predicted = y_pred3[i]
#     status = "✅" if actual == predicted else "❌"
#     print(f"{status} Actual: {actual:25s} | Predicted: {predicted}")

import requests
import json

def ask_ollama(merchant_name, amount):
    prompt = f"""You are a bank transaction categorizer for Indian UPI payments.

Merchant: {merchant_name}
Amount: ₹{amount}

Categorize this transaction. Pick EXACTLY one type and one category.

Types: Expenses, Income, Savings
Categories: Food Outside, Groceries, Transportation, Housing, 
Body Care & Medicine, Utilities, Clothing, Fun & Vacation, 
Play Outside, Media, Subscription, Stock Portfolio, Mutual Fund,
Employment(Net), Cook Salary, Cleaner Salary, Side Hustle(Net), Money Return

Here are some examples:
Merchant: ZOMATO, Amount: ₹450 → {{"type": "Expenses", "category": "Food Outside"}}
Merchant: SHELL, Amount: ₹600 → {{"type": "Expenses", "category": "Transportation"}}
Merchant: Blinkit, Amount: ₹320 → {{"type": "Expenses", "category": "Groceries"}}
Merchant: NOBROKER, Amount: ₹15000 → {{"type": "Expenses", "category": "Housing"}}
Merchant: Groww, Amount: ₹5000 → {{"type": "Savings", "category": "Mutual Fund"}}

Now categorize this:
Merchant: {merchant_name}, Amount: ₹{amount}

Respond ONLY with JSON, nothing else:

Respond ONLY with JSON, nothing else:
{{"type": "...", "category": "..."}}"""
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
            })
        text = response.json()["response"]
        return json.loads(text)
    except:
        return None


def categorize_merchant(merchant_name, amount):
    result = ask_ollama(merchant_name, amount)
    
    if result:
        print(f"\n🤖 Ollama suggests: {result['type']} → {result['category']}")
        confirm = input("Sahi hai? (y/n): ").strip().lower()
        
        if confirm == 'y':
            # Save to CATEGORY_MAP.json
            with open("CATEGORY_MAP.json", "r") as f:
                data = json.load(f)
            data[merchant_name] = result
            with open("CATEGORY_MAP.json", "w") as f:
                json.dump(data, f, indent=4)
            print(f"✅ Saved: {merchant_name} → {result['category']}")
            return result
        else:
            print("Manual input pe jaate hain...")
            return None   # None = manual fallback
    else:
        return None   # Ollama failed = manual fallback
    

if __name__ == "__main__":
    tests = [("THIRD WAVE COFFEE", 280), ("SHELL", 500), ("APOLLO PHARMACY", 1200), ("SWIGGY", 350), ("NOBROKER", 15000)]

    for name, amt in tests:
        result = ask_ollama(name, amt)
        print(f"{name}: {result}")

    categorize_merchant("DOMINOS", 450)