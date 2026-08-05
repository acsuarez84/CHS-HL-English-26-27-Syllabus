"""Read a generated QR grid back to text, to prove the encoder is correct."""
import qr

def decode(grid, ver, ec, mask):
    size = len(grid)
    res = [[False]*size for _ in range(size)]
    def block(r,c,h,w):
        for dr in range(h):
            for dc in range(w):
                if 0<=r+dr<size and 0<=c+dc<size: res[r+dr][c+dc]=True
    block(0,0,9,9); block(0,size-8,9,8); block(size-8,0,8,9)
    for i in range(size): res[6][i]=True; res[i][6]=True
    for r in qr.ALIGN[ver]:
        for c in qr.ALIGN[ver]:
            if not (r<9 and c<9) and not (r<9 and c>size-10) and not (r>size-10 and c<9):
                block(r-2,c-2,5,5)
    mf = [lambda r,c:(r+c)%2==0, lambda r,c:r%2==0, lambda r,c:c%3==0,
          lambda r,c:(r+c)%3==0, lambda r,c:(r//2+c//3)%2==0,
          lambda r,c:(r*c)%2+(r*c)%3==0, lambda r,c:((r*c)%2+(r*c)%3)%2==0,
          lambda r,c:((r+c)%2+(r*c)%3)%2==0][mask]
    bits=[]; up=True; col=size-1
    while col>0:
        if col==6: col-=1
        for r in (range(size-1,-1,-1) if up else range(size)):
            for c in (col,col-1):
                if not res[r][c]:
                    bits.append(1 if (grid[r][c] ^ mf(r,c)) else 0)
        up=not up; col-=2
    cws=[int("".join(map(str,bits[i:i+8])),2) for i in range(0,len(bits)//8*8,8)]
    e,b1,d1,b2,d2 = qr.BLOCKS[ver][ec]
    nblk=b1+b2; dlens=[d1]*b1+[d2]*b2
    blocks=[[] for _ in range(nblk)]
    i=0
    for pos in range(max(dlens)):
        for bi in range(nblk):
            if pos < dlens[bi]:
                blocks[bi].append(cws[i]); i+=1
    data=[x for b in blocks for x in b]
    bs="".join(f"{c:08b}" for c in data)
    mode=int(bs[0:4],2); cc = 8 if ver<10 else 16
    n=int(bs[4:4+cc],2); p=4+cc
    out=bytearray()
    for k in range(n):
        out.append(int(bs[p+k*8:p+k*8+8],2))
    return mode, n, out.decode("utf-8","replace")

URL="https://acsuarez84.github.io/CHS-HL-English-26-27-Syllabus/"
g,ver,mask = qr.build(URL,"M")
mode,n,text = decode(g,ver,"M",mask)
print(f"mode={mode} (4=byte)  length={n}")
print(f"decoded : {text!r}")
print(f"MATCHES : {text == URL}")
