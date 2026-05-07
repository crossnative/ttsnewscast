from newspaper import Article

url = 'https://knightcolumbia.org/content/ai-as-normal-technology'
article = Article(url)

article.download()
article.parse()

print(article.title)
print()
print(article.authors)
print()
print(article.publish_date)
print()
print(article.top_image)

article.nlp()
print(article.keywords)
print(article.summary)
print()

print(article.text)

text = article.title + "\n" + article.text