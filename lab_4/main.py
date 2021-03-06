"""
Lab 4
"""
import re
from ngrams.ngram_trie import NGramTrie


def tokenize_by_sentence(text: str) -> tuple:
    if not isinstance(text, str):
        raise ValueError

    sentences = re.split(r'[.?!]\W', text)
    tokens = []
    for sentence in sentences:
        list_tokens = re.sub('[^a-z \n]', '', sentence.lower()).split()
        if not list_tokens:
            continue
        tokens += list_tokens + ['<END>']
    return tuple(tokens)


class WordStorage:
    def __init__(self):
        self.storage = {}

    def _put_word(self, word: str):
        if not isinstance(word, str) or not word:
            raise ValueError

        if word not in self.storage:
            self.storage[word] = len(self.storage) + 1
        return len(self.storage)

    def get_id(self, word: str) -> int:
        if not isinstance(word, str) or not word:
            raise ValueError

        if word not in self.storage:
            raise KeyError
        return self.storage[word]

    def get_word(self, word_id: int) -> str:
        if not isinstance(word_id, int):
            raise ValueError

        if word_id not in self.storage.values():
            raise KeyError
        for key, value in self.storage.items():
            if value == word_id:
                res = key
        return res

    def update(self, corpus: tuple):
        if not isinstance(corpus, tuple) or not tuple:
            raise ValueError

        for word in corpus:
            self._put_word(word)


def encode_text(storage: WordStorage, text: tuple) -> tuple:
    if not isinstance(text, tuple) or not all(isinstance(word, str) for word in text) \
            or not isinstance(storage, WordStorage):
        raise ValueError

    encoded_text = []
    for word in text:
        encoded_text.append(storage.get_id(word))
    return tuple(encoded_text)


class NGramTextGenerator: # pylint: disable=too-few-public-methods
    def __init__(self, word_storage: WordStorage, n_gram_trie: NGramTrie):
        self._word_storage = word_storage
        self._n_gram_trie = n_gram_trie

    def _generate_next_word(self, context: tuple) -> int:
        if not isinstance(context, tuple) or not all(isinstance(num, int) for num in context)\
                or self._n_gram_trie.size != len(context) + 1:
            raise ValueError

        word_freq = 0
        word_ind = 0
        for n_gram, freq in self._n_gram_trie.n_gram_frequencies.items():
            if n_gram[:len(context)] == context and freq > word_freq:
                word_freq = freq
                word_ind = n_gram[-1]
        if not word_freq:
            max_freq_word = max(self._n_gram_trie.uni_grams.values())
            return list(word[0] for word, value in self._n_gram_trie.uni_grams.items() if value == max_freq_word)[0]
        return word_ind

    def _generate_sentence(self, context: tuple) -> tuple:
        if not isinstance(context, tuple) or not all(isinstance(num, int) for num in context):
            raise ValueError

        sentence = list(context)
        for _ in range(20):
            sentence.append(NGramTextGenerator._generate_next_word(self, tuple(sentence[-(self._n_gram_trie.size-1):])))
            if sentence[-1] == self._word_storage.get_id('<END>'):
                break
        if self._word_storage.get_id('<END>') not in sentence:
            sentence.append(self._word_storage.get_id('<END>'))
        return tuple(sentence)

    def generate_text(self, context: tuple, number_of_sentences: int) -> tuple:
        if not isinstance(context, tuple) or not all(isinstance(num, int) for num in context)\
                or not isinstance(number_of_sentences, int):
            raise ValueError

        generated_text = list(context)
        for _ in range(number_of_sentences):
            sentence = self._generate_sentence(tuple(generated_text[-(self._n_gram_trie.size-1):]))
            generated_text.extend(sentence[self._n_gram_trie.size-1:])
        return tuple(generated_text)


class LikelihoodBasedTextGenerator(NGramTextGenerator): # pylint: disable=too-few-public-methods

    def _calculate_maximum_likelihood(self, word: int, context: tuple) -> float:
        if not isinstance(word, int) or not isinstance(context, tuple)\
                or not all(isinstance(num, int) for num in context) or len(context)+1 != self._n_gram_trie.size:
            raise ValueError

        context_freq = 0
        for num, freq in self._n_gram_trie.n_gram_frequencies.items():
            if context == num[:len(context)]:
                context_freq += freq
        context_2 = tuple(list(context) + [word])
        likelihood = 0
        if context_freq:
            likelihood = self._n_gram_trie.n_gram_frequencies.get(context_2, 0) / context_freq
        return likelihood

    def _generate_next_word(self, context: tuple) -> int:
        if not isinstance(context, tuple) or len(context) + 1 != self._n_gram_trie.size\
                or not all(isinstance(num, int) for num in context) or context[0] > len(self._word_storage.storage):
            raise ValueError

        likelihood = 0
        generated_word = 0
        for word in self._word_storage.storage.values():
            likelihood_0 = self._calculate_maximum_likelihood(word, context)
            if likelihood_0 > likelihood:
                likelihood = likelihood_0
                generated_word = word
        return generated_word


class BackOffGenerator(NGramTextGenerator): # pylint: disable=too-few-public-methods

    def __init__(self, word_storage: WordStorage, n_gram_trie: NGramTrie, *args):
        super().__init__(word_storage, n_gram_trie)
        pass

    def _generate_next_word(self, context: tuple) -> int:
        pass


def decode_text(storage: WordStorage, encoded_text: tuple) -> tuple:
    if not isinstance(encoded_text, tuple) or not isinstance(storage, WordStorage):
        raise ValueError

    decoded_text = []
    decoded_sentence = []
    for num in encoded_text:
        word = storage.get_word(num)
        if word != '<END>':
            decoded_sentence.append(word)
        else:
            decoded_text.append(" ".join(decoded_sentence))
            decoded_sentence = []
    for index, sentence in enumerate(decoded_text):
        decoded_text.pop(index)
        if sentence:
            changed_sentence = sentence[0].upper() + sentence[1:]
            decoded_text.insert(index, changed_sentence)
    return tuple(decoded_text)


def save_model(model: NGramTextGenerator, path_to_saved_model: str):
    pass


def load_model(path_to_saved_model: str) -> NGramTextGenerator:
    pass
