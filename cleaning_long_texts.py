import json
import re
import numpy as np

def shorten_by_removing_plain_text_keep_tags(text, max_length):
    if len(text) <= max_length:
        return text, False
    tokens = re.split(r'(\[[^\]]+\])', text)
    is_tag = [bool(re.fullmatch(r'\[[^\]]+\]', t)) for t in tokens]
    lengths = [len(t) for t in tokens]
    total_len = sum(lengths)
    if total_len <= max_length:
        return text, False
    plain_segments = [(i, lengths[i]) for i in range(len(tokens)) if not is_tag[i] and lengths[i] > 0]
    if not plain_segments:
        result, cur = [], 0
        for t in tokens:
            if cur + len(t) <= max_length:
                result.append(t)
                cur += len(t)
            else:
                break
        shortened = ''.join(result).rstrip() + ' ...'
        return shortened, True
    plain_segments.sort(key=lambda x: x[1], reverse=True)
    tokens_copy = tokens[:]
    cur_len = total_len
    for idx, ln in plain_segments:
        if cur_len <= max_length:
            break
        tokens_copy[idx] = ''
        cur_len -= ln
    if cur_len > max_length:
        for i in range(len(tokens_copy)):
            if not is_tag[i] or not tokens_copy[i]:
                continue
            if cur_len <= max_length:
                break
            seg = tokens_copy[i]
            seg_len = len(seg)
            trim = min(cur_len - max_length, seg_len)
            keep_left = seg_len // 2 - trim // 2
            keep_right = seg_len - (trim + keep_left)
            new_seg = seg[:keep_left] + ' ... ' + seg[-keep_right:]
            cur_len -= (seg_len - len(new_seg))
            tokens_copy[i] = new_seg
    shortened = ''.join(tokens_copy).strip()
    if len(shortened) < len(text):
        if not shortened.endswith(' ...'):
            shortened += ' ...'
        return shortened, True
    return text, False

if __name__ == "__main__":
    with open("dataset_modified.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data if isinstance(data, list) else next(v for v in data.values() if isinstance(v, list))
    lengths = [len(i["text"]) for i in items if "text" in i]
    max_len = int(np.percentile(lengths, 95))
    for i in items:
        if "text" in i:
            short, changed = shorten_by_removing_plain_text_keep_tags(i["text"], max_len)
            if changed:
                i["text"] = short
    with open("dataset_modified_shortened.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
