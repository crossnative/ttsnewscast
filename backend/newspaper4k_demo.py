from newspaper import Article

url = 'https://knightcolumbia.org/content/ai-as-normal-technology'
article = Article(url)

article.download()
article.parse()

print(article.title)
print()
print(article.text)

text = article.title + "\n" + article.text