# 量子力学II レポート課題 答案(ドラフト)

**学籍番号:4143　氏名:二川 航大** ／ **提出期限:2026年7月14日(火)** ／ A4用紙4枚・要出典

> **注意(必読)**
> - 元のレポート課題PDFは日本語部分が文字化けするため、問題文の細部は完全には読み取れていません。**下記は問題文を「3つのスピン1/2の合成」「磁場中2p状態のゼーマン効果」「選択論述」と解釈した答案です。** 提出前に必ずPDF原本で設問の正確な要求を確認してください。
> - これは**学習用のドラフト**です。内容を理解したうえで、自分の言葉で書き直し・図の追加を行って提出してください。出典は末尾の参考文献に記載しています。

---

## 第1問:3つのスピン1/2の合成

### 方針
3個のスピン1/2($\hat{\boldsymbol s}_1,\hat{\boldsymbol s}_2,\hat{\boldsymbol s}_3$)の合成スピン $\hat{\boldsymbol S}=\hat{\boldsymbol s}_1+\hat{\boldsymbol s}_2+\hat{\boldsymbol s}_3$ の固有状態を求める。まず2個を合成し、そこに3個目を加える。

### 2個の合成
$$\tfrac12\otimes\tfrac12 = 1\oplus 0$$
- 三重項($S_{12}=1$):$|1,1\rangle=|\!\uparrow\uparrow\rangle,\quad |1,0\rangle=\tfrac{1}{\sqrt2}(|\!\uparrow\downarrow\rangle+|\!\downarrow\uparrow\rangle),\quad |1,-1\rangle=|\!\downarrow\downarrow\rangle$
- 一重項($S_{12}=0$):$|0,0\rangle=\tfrac{1}{\sqrt2}(|\!\uparrow\downarrow\rangle-|\!\downarrow\uparrow\rangle)$

### 3個目を加える
$$\tfrac12\otimes\tfrac12\otimes\tfrac12=(1\oplus0)\otimes\tfrac12=\underbrace{\tfrac32}_{4}\oplus\underbrace{\tfrac12}_{2}\oplus\underbrace{\tfrac12}_{2}$$
次元は $2^3=8=4+2+2$ で一致する。$j=\tfrac12$ は**2組**現れる。

#### (a) $S=\tfrac32$(四重項・完全対称)
最高重み状態から $\hat S_-=\hat s_{1-}+\hat s_{2-}+\hat s_{3-}$ を作用させて構成する。
$$
\begin{aligned}
\left|\tfrac32,\tfrac32\right\rangle &= |\!\uparrow\uparrow\uparrow\rangle\\
\left|\tfrac32,\tfrac12\right\rangle &= \tfrac{1}{\sqrt3}\left(|\!\uparrow\uparrow\downarrow\rangle+|\!\uparrow\downarrow\uparrow\rangle+|\!\downarrow\uparrow\uparrow\rangle\right)\\
\left|\tfrac32,-\tfrac12\right\rangle &= \tfrac{1}{\sqrt3}\left(|\!\downarrow\downarrow\uparrow\rangle+|\!\downarrow\uparrow\downarrow\rangle+|\!\uparrow\downarrow\downarrow\rangle\right)\\
\left|\tfrac32,-\tfrac32\right\rangle &= |\!\downarrow\downarrow\downarrow\rangle
\end{aligned}
$$

#### (b) $S=\tfrac12$(第1組:$S_{12}=1$ 由来、混合対称)
$j_1=1$ と $j_2=\tfrac12$ の合成のClebsch–Gordan係数より
$$
\begin{aligned}
\left|\tfrac12,\tfrac12\right\rangle_{S_{12}=1} &= \sqrt{\tfrac23}\,|1,1\rangle|\!\downarrow\rangle-\sqrt{\tfrac13}\,|1,0\rangle|\!\uparrow\rangle\\
&= \sqrt{\tfrac23}\,|\!\uparrow\uparrow\downarrow\rangle-\tfrac{1}{\sqrt6}\left(|\!\uparrow\downarrow\uparrow\rangle+|\!\downarrow\uparrow\uparrow\rangle\right)\\
\left|\tfrac12,-\tfrac12\right\rangle_{S_{12}=1} &= \sqrt{\tfrac13}\,|1,0\rangle|\!\downarrow\rangle-\sqrt{\tfrac23}\,|1,-1\rangle|\!\uparrow\rangle\\
&= \tfrac{1}{\sqrt6}\left(|\!\uparrow\downarrow\downarrow\rangle+|\!\downarrow\uparrow\downarrow\rangle\right)-\sqrt{\tfrac23}\,|\!\downarrow\downarrow\uparrow\rangle
\end{aligned}
$$

#### (c) $S=\tfrac12$(第2組:$S_{12}=0$ 由来、1・2に関し反対称)
$$
\begin{aligned}
\left|\tfrac12,\tfrac12\right\rangle_{S_{12}=0} &= |0,0\rangle|\!\uparrow\rangle=\tfrac{1}{\sqrt2}\left(|\!\uparrow\downarrow\uparrow\rangle-|\!\downarrow\uparrow\uparrow\rangle\right)\\
\left|\tfrac12,-\tfrac12\right\rangle_{S_{12}=0} &= |0,0\rangle|\!\downarrow\rangle=\tfrac{1}{\sqrt2}\left(|\!\uparrow\downarrow\downarrow\rangle-|\!\downarrow\uparrow\downarrow\rangle\right)
\end{aligned}
$$

### 結論
3つのスピン1/2の合成は $S=\tfrac32$ の四重項1組と $S=\tfrac12$ の二重項2組に分かれる($\mathbf 2\otimes\mathbf 2\otimes\mathbf 2=\mathbf 4\oplus\mathbf 2\oplus\mathbf 2$)。$S=\tfrac32$ は完全対称、$S=\tfrac12$ の2組は混合対称性をもつ。

---

## 第2問:磁場 $B$(z方向)中の2p状態のエネルギー(1次摂動)

### 摂動ハミルトニアン
一様磁場 $\boldsymbol B=B\hat z$ 中で、電子の磁気モーメント $\boldsymbol\mu=-\dfrac{\mu_B}{\hbar}(\hat{\boldsymbol L}+g_s\hat{\boldsymbol S})$ との相互作用は
$$
\hat H'=-\boldsymbol\mu\cdot\boldsymbol B=\frac{\mu_B B}{\hbar}\left(\hat L_z+g_s\hat S_z\right)\simeq\frac{\mu_B B}{\hbar}\left(\hat L_z+2\hat S_z\right),
\qquad \mu_B=\frac{e\hbar}{2m_e}.
$$
2p状態は $l=1,\,s=\tfrac12$ で、軌道3重 × スピン2重 = **6重に縮退**しているので、縮退のある1次摂動論を用いる。

### スピン軌道相互作用を無視した場合(または強磁場極限)
良い基底は $|m_l,m_s\rangle$。$\hat L_z+2\hat S_z$ はこの基底で既に対角なので、摂動行列も対角となり、1次エネルギーは
$$
\Delta E^{(1)}=\mu_B B\,(m_l+2m_s).
$$

| $m_l$ | $m_s$ | $m_l+2m_s$ | $\Delta E^{(1)}$ |
|:---:|:---:|:---:|:---:|
| $+1$ | $+\tfrac12$ | $+2$ | $+2\mu_B B$ |
| $0$ | $+\tfrac12$ | $+1$ | $+\mu_B B$ |
| $-1$ | $+\tfrac12$ | $0$ | $0$ |
| $+1$ | $-\tfrac12$ | $0$ | $0$ |
| $0$ | $-\tfrac12$ | $-1$ | $-\mu_B B$ |
| $-1$ | $-\tfrac12$ | $-2$ | $-2\mu_B B$ |

すなわち $2p$ の準位は $\{+2,+1,0,0,-1,-2\}\mu_B B$ の5本(中央は2重縮退)に分裂する。

### 参考:弱磁場極限(スピン軌道相互作用が支配的な場合=異常ゼーマン効果)
スピン軌道結合が磁気項より大きいときは良い基底が $|j,m_j\rangle$ となり、
$$
\Delta E^{(1)}=g_J\,\mu_B B\,m_j,\qquad
g_J=1+\frac{j(j+1)-l(l+1)+s(s+1)}{2j(j+1)}.
$$
2p では
$$
2p_{3/2}:\ g_J=\tfrac43\Rightarrow\Delta E=\tfrac43\mu_B B\,m_j\ (m_j=\pm\tfrac32,\pm\tfrac12),\qquad
2p_{1/2}:\ g_J=\tfrac23\Rightarrow\Delta E=\tfrac23\mu_B B\,m_j\ (m_j=\pm\tfrac12).
$$

### 結論
磁場中の2p状態のエネルギーは1次摂動で $m_l,m_s$(または $m_j$)に応じて分裂する。スピン軌道相互作用を無視すれば $\Delta E=\mu_B B(m_l+2m_s)$、弱磁場でスピン軌道結合を考慮すれば $\Delta E=g_J\mu_B B\,m_j$(ランデのg因子)となる。**どちらを問われているかは設問の前提を確認すること。**

---

## 第3問(選択):プランク定数の値が2倍の世界

### 3.1 論点:「$\hbar$ を2倍にする」とは何を意味するか
プランク定数 $\hbar$ は $[\mathrm{J\cdot s}]$ の次元を持ち、その数値は単位系に依存する。よって「$\hbar$ を2倍にする」操作はそのままでは一意でない。物理的に観測可能なのは**無次元量**だけである(あらゆる測定は「対象/基準」という無次元比を返す)。この立場を徹底したのが Duff–Okun–Veneziano の "Trialogue" [1] で、Duff は「基礎的な次元付き定数の個数は0」とまで論じる。以下ではまず、他の定数($e,\,m_e,\,c,\,\varepsilon_0,\,G,\,k_B$)を固定して $\hbar\to2\hbar$ とする素朴な解釈でスケーリングを検証し、その後この解釈の限界を考察する。

### 3.2 スケーリングの検証(他の定数を固定し $\hbar\to2\hbar$)
本質は、電磁相互作用の強さを表す**微細構造定数**が半分になることである:
$$\alpha=\frac{e^2}{4\pi\varepsilon_0\hbar c}\propto\hbar^{-1}\ \Rightarrow\ \alpha\to\tfrac12\alpha\simeq\frac{1}{274}.$$
水素原子の基本量の次元解析より
$$a_0=\frac{4\pi\varepsilon_0\hbar^2}{m_e e^2}\propto\hbar^{2},\qquad
E_{\text{Ry}}=\frac{m_e e^4}{2(4\pi\varepsilon_0)^2\hbar^2}\propto\hbar^{-2},\qquad
\lambda_{\text{th}}=\frac{h}{\sqrt{2\pi m_e k_B T}}\propto\hbar.$$

| 物理量 | $\hbar$ 依存性 | 倍率($\hbar\to2\hbar$) |
|---|:---:|:---:|
| 微細構造定数 $\alpha$ | $\hbar^{-1}$ | $\times\tfrac12$ |
| ボーア半径 $a_0$ | $\hbar^{2}$ | $\times4$ |
| 束縛エネルギー(Rydberg) | $\hbar^{-2}$ | $\times\tfrac14$ |
| 微細構造分裂/主構造 $(\propto\alpha^2)$ | $\hbar^{-2}$ | $\times\tfrac14$ |
| 零点エネルギー $\tfrac12\hbar\omega$ | $\hbar$ | $\times2$ |
| 熱的ド・ブロイ波長 $\lambda_{\text{th}}$ | $\hbar$ | $\times2$ |
| 量子縮退温度 $T_{\text{deg}}\propto\hbar^2 n^{2/3}/m k_B$ | $\hbar^{2}$ | $\times4$ |
| Wienピーク波長 $\lambda_{\max}\propto h$ | $\hbar$ | $\times2$ |
| Stefan–Boltzmann係数 $\sigma\propto\hbar^{-3}$ | $\hbar^{-3}$ | $\times\tfrac18$ |
| Chandrasekhar質量 $M_{\text{Ch}}\propto(\hbar c/G)^{3/2}$ | $\hbar^{3/2}$ | $\times2.83$ |

### 3.3 帰結の考察
- **原子・物質**:原子は約4倍に膨らみ束縛エネルギーは1/4。物質は「柔らかく」なるが、$\alpha\ll1$ は保たれるため物質の安定性は失われない。
- **相対論効果の相対的縮小**:微細構造は主構造に対して $\alpha^2$ で効くため1/4に。スペクトルはより理想的な水素型に近づく。
- **量子効果の巨視化**:$\lambda_{\text{th}}\propto\hbar$、縮退温度 $\propto\hbar^2$ が増大し、BEC・電子縮退・超伝導などがより高温で起こる。不確定性下限 $\hbar/2$ も2倍で、古典極限 $\hbar\to0$ から一層遠ざかる。
- **熱輻射・天体**:黒体輻射のピークは長波長側へ($\lambda_{\max}$ 2倍)、全放射は $\sigma\propto\hbar^{-3}$ で1/8。白色矮星の質量上限 $M_{\text{Ch}}\propto\hbar^{3/2}$ は約2.83倍に増える。

### 3.4 検証の限界と本質的考察
3.2 の倍率はすべて**単位系に依存する**言明である。もし $\alpha$ をはじめとする無次元定数(電子・陽子質量比 $m_e/m_p$ 等)を**すべて不変に保ったまま** $\hbar$ だけを2倍にしたなら、あらゆる測定は無次元比を返すため**いかなる実験でもこの世界を我々の世界と区別できない**——それは単なる単位の取り替えにすぎない [1][2]。したがって「$\hbar$ 2倍の世界」が真に別世界となるのは、その操作が $\alpha$ 等の無次元量の変化を伴う場合に限られる。3.2 で $\alpha\to\alpha/2$ となったのは、$e,c,\varepsilon_0$ 固定という約束が無次元量 $\alpha$ を変化させたからこそである。

基礎定数が実際に変動しうるかは活発な研究対象であり、Uzan のレビュー [2] は理論的動機(大統一・余剰次元・スカラー場)と観測制約を総括している。観測的には $\alpha$ の時間変化は極めて小さく、地質学的(Oklo天然原子炉)・宇宙論的制約から $|\Delta\alpha/\alpha|\lesssim10^{-6}$ 程度に抑えられている [3]。

### 結論
素朴には $\hbar\to2\hbar$ で $\alpha$ が半減し、原子は4倍・束縛エネルギー1/4・量子効果の巨視化・$M_{\text{Ch}}$ 約2.83倍等の帰結を得る。しかし物理的に意味を持つのは無次元定数の変化のみであり、$\alpha$ 等を固定したままの「$\hbar$ 2倍」は観測不能な単位変更にすぎない。**すなわち本問の本質は「$\hbar$ の値」ではなく「$\alpha$ が半分の世界」を論じることにある。**

---

## 参考文献

1. M. J. Duff, L. B. Okun, G. Veneziano, "Trialogue on the number of fundamental constants," JHEP **03** (2002) 023. arXiv:physics/0110060. https://arxiv.org/abs/physics/0110060
2. J.-P. Uzan, "The fundamental constants and their variation: observational status and theoretical motivations," Rev. Mod. Phys. **75** (2003) 403. arXiv:hep-ph/0205340. https://arxiv.org/abs/hep-ph/0205340
3. Fine-structure constant — Wikipedia. https://en.wikipedia.org/wiki/Fine-structure_constant
4. ゼーマン効果 — Wikipedia. https://ja.wikipedia.org/wiki/%E3%82%BC%E3%83%BC%E3%83%9E%E3%83%B3%E5%8A%B9%E6%9E%9C
5. 外部磁場におかれた水素原子のゼーマン効果 — 生命系のための理工学基礎. https://rikei-jouhou.com/zeeman-effect/
6. 軌道角運動量とスピンの合成 / 角運動量の合成 — EMANの量子力学. https://eman-physics.net/quantum/coupling3.html , https://eman-physics.net/quantum/coupling.html
7. 3つ,4つのスピン1/2粒子の合成 — 物理のかぎしっぽ. https://hooktail.sub.jp/quantum/34SpinGousei/

> より詳細なトピック別出典は [`../参考資料/量子力学II_参考資料.md`](../参考資料/量子力学II_参考資料.md) を参照。
