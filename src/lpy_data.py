import os, re, csv

out_dir = "/home/ec2-user/project/lucaprot/LucaProt/dataset/cress/protein/binary_class"
os.makedirs(out_dir, exist_ok=True)

files = {
    "train": "/home/ec2-user/project/data/train.fasta",
    "dev":   "/home/ec2-user/project/data/val.fasta",
    "test":  "/home/ec2-user/project/data/test.fasta",
}

def read_fasta(path):
    header, seq = None, []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    yield header, "".join(seq)
                header = line[1:]
                seq = []
            else:
                seq.append(line)
        if header is not None:
            yield header, "".join(seq)

for split, fasta in files.items():
    out_csv = os.path.join(out_dir, f"{split}_with_pdb_emb.csv")
    with open(out_csv, "w", newline="") as w:
        writer = csv.writer(w)
        writer.writerow(["prot_id","seq","seq_len","pdb_filename","ptm","mean_plddt","emb_filename","label","source"])
        for h, s in read_fasta(fasta):
            prot_id = h.split()[0]  # 去掉描述
            m = re.search(r"\|label=([01])\b", h)
            if not m:
                raise ValueError(f"header里找不到label: {h}")
            label = m.group(1)
            writer.writerow([prot_id, s, len(s), "", "", "", "", label, "custom"])
print("done")