# 量子力学II レポート課題 答案(ドラフト)

**提出期限:2026年7月14日(火)** ／ A4用紙4枚・要出典

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

## 第3問(選択):(1) 位置と運動量の同時測定は可能か

> 3つのテーマから1つを選ぶ設問。ここでは (1) を選んで論述する。(2)(3) の要点は末尾に添える。

### 主張
**位置を誤差0で測定すること自体は原理的に可能だが、そのとき運動量は完全に不定になり、位置と運動量を同時に誤差0で測定することはできない。** これは測定器の精度の問題ではなく、量子力学の原理に由来する制限である。

### 論拠
位置演算子 $\hat x$ と運動量演算子 $\hat p$ は交換しない:
$$[\hat x,\hat p]=i\hbar\neq0.$$
Robertson の不確定性関係
$$\Delta A\,\Delta B\ge\frac12\left|\langle[\hat A,\hat B]\rangle\right|$$
に代入すると
$$\Delta x\,\Delta p\ge\frac{\hbar}{2}.$$
非可換な2つの物理量は**同時固有状態を持たない**ため、両者を同時に確定値に定めることはできない。位置を誤差0で測る($\Delta x\to0$)と、上式より $\Delta p\to\infty$ となり、直後に運動量を測ると結果は完全にランダムになる。位置の固有状態 $|x_0\rangle$(デルタ関数 $\delta(x-x_0)$)を運動量表示すると全運動量にわたって一様に広がっており、運動量が定まらないことと整合する。

### 補足
- 位置**だけ**、あるいは運動量**だけ**なら、それぞれ原理的に誤差0で測定可能(片方を犠牲にすれば良い)。
- 可換な物理量(例:$\hat L^2$ と $\hat L_z$)なら同時固有状態が存在し、同時に確定値をとれる。位置と運動量が同時測定できないのは両者が非可換だからである。

### (他テーマを選ぶ場合の要点)
- **(2) トンネル効果とスイッチングデバイス/集積度の限界**:トランジスタの微細化でゲート絶縁膜が薄くなるとトンネル効果でリーク電流が生じ、消費電力・発熱が増大する。これが微細化(ムーアの法則)の物理的限界の一因。逆にトンネル効果を積極利用したトンネルダイオード/トンネルFETはスイッチングに応用される。
- **(3) プランク定数が2倍の世界**:ド・ブロイ波長 $\lambda=h/p$ と不確定性 $\hbar/2$ が2倍になり量子効果が巨視化する。ボーア半径 $a_B\propto\hbar^2$ は4倍、原子の束縛エネルギー $\propto1/\hbar^2$ は1/4になるなど、原子の大きさ・安定性が大きく変わる。

---

## 参考文献

1. ゼーマン効果 — Wikipedia. https://ja.wikipedia.org/wiki/%E3%82%BC%E3%83%BC%E3%83%9E%E3%83%B3%E5%8A%B9%E6%9E%9C
2. 外部磁場におかれた水素原子のゼーマン効果 — 生命系のための理工学基礎. https://rikei-jouhou.com/zeeman-effect/
3. 【やさしい量子力学】異常ゼーマン効果. https://taido.blog/anomalous-zeeman-effect/
4. 軌道角運動量とスピンの合成 / 角運動量の合成 — EMANの量子力学. https://eman-physics.net/quantum/coupling3.html , https://eman-physics.net/quantum/coupling.html
5. 3つ,4つのスピン1/2粒子の合成 — 物理のかぎしっぽ. https://hooktail.sub.jp/quantum/34SpinGousei/
6. ポアソン括弧 — Wikipedia(交換関係と量子化). https://ja.wikipedia.org/wiki/%E3%83%9D%E3%82%A2%E3%82%BD%E3%83%B3%E6%8B%AC%E5%BC%A7
7. ムーアの法則 — Wikipedia. https://ja.wikipedia.org/wiki/%E3%83%A0%E3%83%BC%E3%82%A2%E3%81%AE%E6%B3%95%E5%89%87
8. ムーアの法則が分かる!半導体微細化のメリットも解説 — 半導体Jobエージェント. https://semiconductor-job.com/moores-law/

> より詳細なトピック別出典は [`../参考資料/量子力学II_参考資料.md`](../参考資料/量子力学II_参考資料.md) を参照。
