#!/usr/bin/env python
# encoding: utf-8

import os
import csv
import argparse


def normalize_prot_id(prot_id):
    """标准化 prot_id，便于跨文件匹配。"""
    return prot_id.strip().lstrip(">")


def read_idx_mapping(idx_csv_file, base_dir):
    """读取 idx.csv，构建 prot_id -> emb_full_path 映射。"""
    prot_to_emb = {}
    with open(idx_csv_file, "r", newline="", encoding="utf-8") as rfp:
        reader = csv.reader(rfp)
        header = next(reader, None)
        if header is None:
            raise ValueError("idx.csv 为空")

        header_l = [h.strip().lower() for h in header]
        idx_col = 0
        prot_col = 1 if len(header) > 1 else None

        if "index" in header_l:
            idx_col = header_l.index("index")
        elif "idx" in header_l:
            idx_col = header_l.index("idx")

        for cand in ["prot_id", "protein_id", "uuid", "id"]:
            if cand in header_l:
                prot_col = header_l.index(cand)
                break

        if prot_col is None:
            raise ValueError("idx.csv 缺少 prot_id/uuid 列，无法按 prot_id 对齐")

        for row_idx, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) <= max(idx_col, prot_col):
                continue

            idx_value = row[idx_col].strip()
            if not idx_value:
                raise ValueError(f"idx.csv 第 {row_idx} 行 index 为空: {row}")

            prot_id = row[prot_col].strip()
            if not prot_id:
                continue

            pt_filename = idx_value if idx_value.endswith(".pt") else f"{idx_value}.pt"
            full_path = combine_base_path(base_dir, pt_filename)
            prot_to_emb[normalize_prot_id(prot_id)] = full_path

    return prot_to_emb


def combine_base_path(base_dir, rel_or_abs_path):
    """如果是绝对路径则原样返回，否则与 base_dir 拼接。"""
    if os.path.isabs(rel_or_abs_path):
        return rel_or_abs_path
    return os.path.normpath(os.path.join(base_dir, rel_or_abs_path))


def fill_emb_filename(idx_csv_file, emb_csv_file, base_dir, output_csv_file):
    prot_to_emb = read_idx_mapping(idx_csv_file, base_dir)

    with open(emb_csv_file, "r", newline="", encoding="utf-8") as rfp:
        reader = csv.reader(rfp)
        rows = list(reader)

    if not rows:
        raise ValueError("emb.csv 为空")

    header = rows[0]
    data_rows = rows[1:]
    header_l = [h.strip().lower() for h in header]

    prot_col = None
    for cand in ["prot_id", "protein_id", "uuid", "id"]:
        if cand in header_l:
            prot_col = header_l.index(cand)
            break
    if prot_col is None:
        raise ValueError("emb.csv 缺少 prot_id/protein_id/uuid/id 列，无法按 prot_id 对齐")

    if "emb_filename" in header:
        emb_col_idx = header.index("emb_filename")
    else:
        header.append("emb_filename")
        emb_col_idx = len(header) - 1

    hit, miss = 0, 0
    for row in data_rows:
        if len(row) <= emb_col_idx:
            row.extend([""] * (emb_col_idx + 1 - len(row)))

        prot_id = row[prot_col].strip() if len(row) > prot_col else ""
        full_path = prot_to_emb.get(normalize_prot_id(prot_id), "")
        row[emb_col_idx] = full_path
        if full_path:
            hit += 1
        else:
            miss += 1

    with open(output_csv_file, "w", newline="", encoding="utf-8") as wfp:
        writer = csv.writer(wfp)
        writer.writerow(header)
        writer.writerows(data_rows)

    print(f"写入完成: {output_csv_file}")
    print(f"按 prot_id 对齐完成: 命中 {hit} 行, 未命中 {miss} 行")


def main():
    parser = argparse.ArgumentParser(description="按 prot_id 对齐：读取 idx.csv 的 index+prot_id，生成 pt 路径并写入 emb.csv 的 emb_filename 列")
    parser.add_argument("--idx_csv", required=True, help="idx.csv 文件路径")
    parser.add_argument("--emb_csv", required=True, help="emb.csv 文件路径")
    parser.add_argument("--base_dir", required=True, help="命令行给定的基础目录，会与 idx.csv 的 index + .pt 拼接")
    parser.add_argument("--output_csv", default=None, help="输出文件路径；不传则覆盖 emb.csv")
    args = parser.parse_args()

    output_csv_file = args.output_csv if args.output_csv else args.emb_csv
    fill_emb_filename(args.idx_csv, args.emb_csv, args.base_dir, output_csv_file)


if __name__ == "__main__":
    main()
