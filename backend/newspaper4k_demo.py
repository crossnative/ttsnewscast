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


from lingua import Language, LanguageDetectorBuilder
# languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
# detector = LanguageDetectorBuilder.from_languages(*languages).build()
detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()
language = detector.detect_language_of(text)
print(language)