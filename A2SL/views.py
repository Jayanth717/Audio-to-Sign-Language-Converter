from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required

import nltk


def home_view(request):
    return render(request, "home.html")


def about_view(request):
    return render(request, "about.html")


def contact_view(request):
    return render(request, "contact.html")


@login_required(login_url="login")
def animation_view(request):
    if request.method == "POST":
        text = request.POST.get("sen", "")
        text = text.strip()

        # Import NLTK pieces inside the view to avoid LazyCorpusLoader state issues
        from nltk.tokenize import word_tokenize
        from nltk.stem import WordNetLemmatizer
        from nltk.corpus import wordnet

        # Ensure required corpora exist (download only if missing)
        try:
            nltk.data.find("taggers/averaged_perceptron_tagger")
            nltk.data.find("corpora/wordnet")
            nltk.data.find("corpora/omw-1.4")
        except LookupError:
            nltk.download("averaged_perceptron_tagger")
            nltk.download("wordnet")
            nltk.download("omw-1.4")

        # Force WordNet to load fully (prevents: _LazyCorpusLoader__args AttributeError)
        _ = wordnet.synsets("test")

        # Tokenize & POS-tag
        words = word_tokenize(text.lower())
        tagged = nltk.pos_tag(words)

        tense = {
            "future": len([w for w in tagged if w[1] == "MD"]),
            "present": len([w for w in tagged if w[1] in ["VBP", "VBZ", "VBG"]]),
            "past": len([w for w in tagged if w[1] in ["VBD", "VBN"]]),
            "present_continuous": len([w for w in tagged if w[1] == "VBG"]),
        }

        # Stopwords list used by the original project
        stop_words = set([
            "mightn't", "re", "wasn", "wouldn", "be", "has", "that", "does", "shouldn", "do",
            "you've", "off", "for", "didn't", "m", "ain", "haven", "weren't", "are", "she's",
            "wasn't", "its", "haven't", "wouldn't", "don", "weren", "s", "you'd", "don't",
            "doesn", "hadn't", "is", "was", "that'll", "should've", "a", "then", "the", "mustn",
            "i", "nor", "as", "it's", "needn't", "d", "am", "have", "hasn", "o", "aren't",
            "you'll", "couldn't", "you're", "mustn't", "didn", "doesn't", "ll", "an", "hadn",
            "whom", "y", "hasn't", "itself", "couldn", "needn", "shan't", "isn", "been", "such",
            "shan", "shouldn't", "aren", "being", "were", "did", "ma", "t", "having", "mightn",
            "ve", "isn't", "won't"
        ])

        # Lemmatize + remove stopwords
        lr = WordNetLemmatizer()
        filtered = []

        for (w, p) in zip(words, tagged):
            if w in stop_words:
                continue

            pos = p[1]
            if pos in ["VBG", "VBD", "VBZ", "VBN", "NN"]:
                filtered.append(lr.lemmatize(w, pos="v"))
            elif pos in ["JJ", "JJR", "JJS", "RBR", "RBS"]:
                filtered.append(lr.lemmatize(w, pos="a"))
            else:
                filtered.append(lr.lemmatize(w))

        words = filtered

        # Apply tense marker words
        probable_tense = max(tense, key=tense.get)

        if probable_tense == "past" and tense["past"] >= 1:
            words = ["before"] + words

        elif probable_tense == "future" and tense["future"] >= 1:
            if "will" not in words:
                words = ["will"] + words

        elif probable_tense == "present" and tense["present_continuous"] >= 1:
            words = ["now"] + words

        # Map words to available animations; fallback to letters if video not found
        final_words = []
        for w in words:
            path = f"{w}.mp4"
            f = finders.find(path)

            if not f:
                # split into letters if no word animation
                for c in w:
                    final_words.append(c)
            else:
                final_words.append(w)

        return render(request, "animation.html", {"words": final_words, "text": text})

    return render(request, "animation.html")


def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("animation")
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            nxt = request.POST.get("next")
            if nxt:
                return redirect(nxt)
            return redirect("animation")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")
