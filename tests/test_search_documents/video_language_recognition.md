# 识别视频语言

## 概述

视频里面的语言分为图片上面打出来的字幕以及人说的话

涉及到的问题分别为： 图片文字的语言分类 以及音频语言分类

## 音频识别

online speech recognition
pip install SpeechRecognition

offline, need to provide language id:
https://pypi.org/project/automatic-speech-recognition/

use paddlespeech if possible, for chinese and english

## 图片语言识别

use google cloud to detect language type in image:
https://github.com/deduced/ml-ocr-lang-detection

Detects and Recognizes text and font language in an image
https://github.com/JAIJANYANI/Language-Detection-in-Image

图片语言文字分类 可以用easyocr实现 加载多个模型 比如 中文加英文加日语 b站其他语言的可能也不怎么受欢迎 最多再加韩语

可以从视频简介 标题 链接里面提取出句子 每个句子进行语言分类 确定要使用的OCR模型 也有可能出现描述语言和视频图片文字语言不一致的情况

wolfram language提供了一个图片分类器 分类出来的结果可能很有意思 可以结合苹果的图片关注区域生成器来结合使用

ImageIdentify[pictureObj]

这个方法还支持subcategory分类 支持多输出 具体看文档

https://www.imageidentify.com/about/how-it-works

wolfram支持cloud deploy 到wolfram cloud不过那样可能不行

## 文本语言识别分类

[lingua](https://github.com/pemistahl/lingua) performs good in short text, can be used in java or kotlin

supporting detecting different languages:
[cld2](https://github.com/ropensci/cld2) containing useful vectors containing text spans [python binding](https://pypi.org/project/pycld2/)

```python
>>> import pycld2 as cld2
>>> text_content = """ A accès aux chiens et aux frontaux qui lui ont été il peut consulter et modifier ses collections et exporter Cet article concerne le pays européen aujourd’hui appelé République française. 
Pour d’autres usages du nom France, Pour une aide rapide et effective, veuiller trouver votre aide dans le menu ci-dessus. 
Welcome, to this world of Data Scientist. Today is a lovely day."""
>>> _, _, _, detected_language = cld2.detect(text_content,  returnVectors=True)
>>> print(detected_language)
((0, 323, 'FRENCH', 'fr'), (323, 64, 'ENGLISH', 'en'))
```

[original cld3](https://github.com/google/cld3) is designed for chromium and it relies on chromium code to run
[official cld3 python bindings](https://pypi.org/project/gcld3/)

additional Python language related library from geeksforgeeks:
[textblob](https://textblob.readthedocs.io/en/dev/) is a natural language processing toolkit
```python
from textblob import TextBlob
text = "это компьютерный портал для гиков. It was a beautiful day ."
lang = TextBlob(text)
print(lang.detect_language())
# ru
```
[langid](https://github.com/saffsd/langid.py) performs good in short text

[textcat (r package)](https://cran.r-project.org/package=textcat)

google language detection library in python: langdetect

javascript:
https://github.com/wooorm/franc

python version of franc:
pyfranc

wlatlang.org provides whatlang-rs as rust package, also whatlang-py as python bindings