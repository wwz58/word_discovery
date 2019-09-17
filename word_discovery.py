from collections import defaultdict, Counter
import math
import re


def build_vocab(lines, out_vocab_txt, max_word_len, min_freq, min_sticky, min_entropy):
    lines = list(lines)
    n_grams = defaultdict(dict)
    n_grams[1] = Counter([char for line in lines for char in list(line)])
    for k, v in n_grams[1].items():
        n_grams[1][k] = {'freq': v}
    for word_len in range(2, max_word_len + 1):
        gram_dic = n_grams[word_len]
        for line in lines:
            for i in range(0, len(line) - word_len):
                gram = line[i:i + word_len]
                if gram not in gram_dic:
                    gram_dic[gram] = {'freq': 1, 'left': {}, 'right': {}}
                else:
                    gram_dic[gram]['freq'] += 1
                    if i > 0:
                        pre = line[i - 1]
                        if pre not in gram_dic[gram]['left']:
                            gram_dic[gram]['left'][pre] = 1
                        else:
                            gram_dic[gram]['left'][pre] += 1
                    if i < len(line) - word_len - 1:
                        post = line[i + word_len]
                        if post not in gram_dic[gram]['right']:
                            gram_dic[gram]['right'][post] = 1
                        else:
                            gram_dic[gram]['right'][post] += 1
    total = sum([len(n_grams[k]) for k in n_grams])
    for word_len in range(2, max_word_len):
        gram_dic = n_grams[word_len]
        for gram in gram_dic:
            sticky = min([total * gram_dic[gram]['freq'] / (n_grams[i][gram[:i]]['freq']
                                                            * n_grams[word_len-i][gram[i:]]['freq']) for i in range(1, word_len)])
            gram_dic[gram]['sticky'] = sticky
            entorpy = min(cacl_entropy(gram_dic[gram][e])
                          for e in ['left', 'right'])
            gram_dic[gram]['entropy'] = entorpy
    for word_len, gram_dic in n_grams.items():
        n_grams[word_len] = {gram: v for gram, v in gram_dic.items() if (
            v['freq'] > min_freq and v.get('sticky', min_sticky[word_len]+1) > min_sticky[word_len] and v.get('entropy', min_entropy+1) > min_entropy)}
    V = [gram for gram_dic in n_grams.values() for gram in gram_dic]
    V.sort(reverse=True, key=lambda w: n_grams[len(w)][w]['freq'])
    with open(out_vocab_txt, 'w') as f:
        f.write('\n'.join(V) + '\n')


def cacl_entropy(neighbour_char_cnt):
    cnts = list(neighbour_char_cnt.values())
    summ = sum(cnts)
    cnts = [c / summ for c in cnts]
    H = 0
    for c in cnts:
        H += -c * math.log(c)
    return H


def read_corpus(corpus_txt):
    with open(corpus_txt) as f:
        for line in f:
            for sub_line in re.split(r'[^\u4e00-\u9fa50-9a-zA-Z ]+', line):
                yield sub_line


def main(corpus_txt, out_vocab_txt, max_word_len=5, min_freq=7, min_sticky=[None, 10, 15, 20, 25], min_entropy=1):
    lines = read_corpus(corpus_txt)
    build_vocab(lines, out_vocab_txt, max_word_len,
                min_freq, min_sticky, min_entropy)
    print('build done')


if __name__ == "__main__":
    # import fire
    # fire.Fire(main)
    main('test.txt', 'test_vocab.txt')
