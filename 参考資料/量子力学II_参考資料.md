# 量子力学II 参考資料集(出典付き)

レポート課題および確認問題(全12回)の各トピックについて、Web上の信頼できる解説・講義ノート等を収集し、要点をまとめたものです。**レポートで引用する際は、下記の出典URLを参考文献として明記してください。**

> 収集日: 2026-07-08

---

## 1. レポート課題 第1問:3つのスピン1/2の合成

### 要点
- 2つのスピン1/2の合成は $\tfrac12 \otimes \tfrac12 = 1 \oplus 0$(三重項 $S=1$ と一重項 $S=0$)。
- 3つ目のスピン1/2を加えると
  $$\tfrac12 \otimes \tfrac12 \otimes \tfrac12 = \left(1 \oplus 0\right)\otimes\tfrac12 = \tfrac32 \;\oplus\; \tfrac12 \;\oplus\; \tfrac12$$
  次元は $2\times2\times2 = 8 = 4\,(j=\tfrac32) + 2 + 2\,(j=\tfrac12\text{ が2組})$。
- $j=\tfrac32$ の四重項は3スピンの入れ替えに対して**完全対称**。$j=\tfrac12$ は2組現れ、これは混合対称性を持つ(全対称・全反対称のどちらでもない)。
- 各状態は昇降演算子 $\hat J_\pm = \hat J_{1\pm}+\hat J_{2\pm}+\hat J_{3\pm}$ を最高重み状態 $|\uparrow\uparrow\uparrow\rangle$ に順に作用させて構成できる。

### 出典
- [軌道角運動量とスピンの合成 — EMANの量子力学](https://eman-physics.net/quantum/coupling3.html)
- [角運動量の合成 — EMANの量子力学](https://eman-physics.net/quantum/coupling.html)
- [3つ,4つのスピン1/2粒子の合成 — 物理のかぎしっぽ](https://hooktail.sub.jp/quantum/34SpinGousei/)
- [スピン,一般化角運動量と角運動量の合成(岡本, PDF)](https://rokamoto.sakura.ne.jp/education/quantum/spin-angular-momentum-coupling20200719B.pdf)

---

## 2. レポート課題 第2問:磁場中の2p状態のエネルギー(ゼーマン効果)

### 要点
- 一様磁場 $\boldsymbol B = B\hat z$ 中の電子の摂動ハミルトニアンは、磁気モーメント $\boldsymbol\mu = -\tfrac{\mu_B}{\hbar}(\hat{\boldsymbol L}+g_s\hat{\boldsymbol S})$ と $H' = -\boldsymbol\mu\cdot\boldsymbol B$ から
  $$\hat H' = \frac{\mu_B B}{\hbar}\left(\hat L_z + g_s \hat S_z\right)\approx \frac{\mu_B B}{\hbar}\left(\hat L_z + 2\hat S_z\right),\qquad \mu_B=\frac{e\hbar}{2m_e}\ (\text{ボーア磁子}).$$
- **スピン軌道相互作用を無視 / 強磁場極限(Paschen–Back)**:良い基底は $|m_l,m_s\rangle$。$\hat L_z+2\hat S_z$ はこの基底で対角なので、1次のエネルギーは $\Delta E = \mu_B B\,(m_l + 2m_s)$。
- **弱磁場極限(異常ゼーマン効果)**:スピン軌道結合が支配的なら良い基底は $|j,m_j\rangle$。1次エネルギーは
  $$\Delta E = g_J\,\mu_B B\, m_j,\qquad g_J = 1 + \frac{j(j+1)-l(l+1)+s(s+1)}{2j(j+1)}\ (\text{ランデの}g\text{因子}).$$
  2p ($l=1, s=\tfrac12$) では $g_{3/2}=\tfrac43$、$g_{1/2}=\tfrac23$。
- ゼーマン効果は縮退したエネルギー準位が磁場で $2J+1$ 本に分裂する現象。

### 出典
- [ゼーマン効果 — Wikipedia](https://ja.wikipedia.org/wiki/%E3%82%BC%E3%83%BC%E3%83%9E%E3%83%B3%E5%8A%B9%E6%9E%9C)
- [外部磁場におかれた水素原子のゼーマン効果 — 生命系のための理工学基礎](https://rikei-jouhou.com/zeeman-effect/)
- [【やさしい量子力学】異常ゼーマン効果](https://taido.blog/anomalous-zeeman-effect/)
- [ゼーマン効果 — 天文学辞典](https://astro-dic.jp/zeeman-effect/)

---

## 3. レポート課題 第3問(選択テーマ)

### (1) 位置と運動量の同時測定 / 不確定性原理
- Robertson の不確定性関係 $\Delta A\,\Delta B \ge \tfrac12|\langle[\hat A,\hat B]\rangle|$。$[\hat x,\hat p]=i\hbar$ より $\Delta x\,\Delta p\ge \hbar/2$。
- 位置を誤差0($\Delta x\to0$)で測ることは原理的には可能だが、そのとき $\Delta p\to\infty$ となり運動量は完全に不定になる。位置と運動量は**同時固有状態を持たない**(非可換)ため、両方を誤差0で同時測定することはできない。装置の精度の問題ではなく原理的な制限。
- 出典:
  - [ポアソン括弧 — Wikipedia](https://ja.wikipedia.org/wiki/%E3%83%9D%E3%82%A2%E3%82%BD%E3%83%B3%E6%8B%AC%E5%BC%A7)(交換関係と量子化)
  - 講義ノート「量子力学Iの復習」(本リポジトリ `講義ノート/量子力学I_復習.pdf`)の不確定性関係の節

### (2) トンネル効果とスイッチングデバイス・集積度の限界
- トランジスタの微細化で絶縁層(ゲート酸化膜)が極薄になると、電子がトンネル効果で通り抜け**リーク電流**が生じ、消費電力・発熱が増大する。これが微細化(ムーアの法則)の物理的限界の一因。
- 一方、トンネル効果を積極的に利用したデバイス(トンネルダイオード、トンネルFET等)はスイッチングやオン/オフ制御に応用される。
- 出典:
  - [ムーアの法則 — Wikipedia](https://ja.wikipedia.org/wiki/%E3%83%A0%E3%83%BC%E3%82%A2%E3%81%AE%E6%B3%95%E5%89%87)
  - [ムーアの法則が分かる!半導体微細化のメリットも解説 — 半導体Jobエージェント](https://semiconductor-job.com/moores-law/)
  - [【歴史】トランジスタ微細化の限界と2000年代における技術的課題(note)](https://note.com/yaandyu0423/n/n2f829463096b)

### (3) プランク定数の値が2倍の世界
- ド・ブロイ波長 $\lambda=h/p$ が2倍になり、量子効果がより大きなスケールで顕在化する。不確定性 $\hbar/2$ も2倍。
- ボーア半径 $a_B = 4\pi\epsilon_0\hbar^2/(m_e e^2)$ は $\hbar^2$ に比例するので**4倍**、水素原子のエネルギー準位 $\propto 1/\hbar^2$ は $1/4$ になるなど、原子のサイズ・束縛エネルギーが劇的に変わる。
- 出典:
  - [井戸型ポテンシャル — Wikipedia](https://ja.wikipedia.org/wiki/%E4%BA%95%E6%88%B8%E5%9E%8B%E3%83%9D%E3%83%86%E3%83%B3%E3%82%B7%E3%83%A3%E3%83%AB)($\hbar$ に対するエネルギー準位のスケーリング)

---

## 4. 確認問題の各回トピック(補助資料)

### 第1-3回:ポアソン括弧・随伴演算子・Levi-Civita記号
- 正準方程式から $\dfrac{dF}{dt}=\{F,H\}$ を導く。量子化ではポアソン括弧 $\{\ ,\ \}$ を交換子 $\tfrac{1}{i\hbar}[\ ,\ ]$ に置き換える。
- $\epsilon_{ijk}\epsilon_{nlm}$ の $3\times3$ 行列式表示、および $n=i$ で縮約した $\epsilon_{ijk}\epsilon_{ilm}=\delta_{jl}\delta_{km}-\delta_{jm}\delta_{kl}$。
- 出典:
  - [ポアソン括弧 — Wikipedia](https://ja.wikipedia.org/wiki/%E3%83%9D%E3%82%A2%E3%82%BD%E3%83%B3%E6%8B%AC%E5%BC%A7)
  - [ポアッソン括弧式 — EMANの解析力学](https://eman-physics.net/analytic/poisson.html)
  - [量子力学を学ぶための解析力学の基礎(国広, 京大, PDF)](https://www2.yukawa.kyoto-u.ac.jp/~teiji.kunihiro/QM_suppl/Cl-Mech-wo-wave.pdf)

### 第4-6回:昇降演算子・球面調和関数・水素原子動径方程式
- $\hat J_\pm|j,m\rangle = \sqrt{j(j+1)-m(m\pm1)}\,\hbar\,|j,m\pm1\rangle$。
- $Y_l^m$ が $\hat L^2$($=l(l+1)\hbar^2$)と $\hat L_z$($=m\hbar$)の同時固有関数であることの確認。
- 出典:
  - [昇降演算子 — Wikipedia](https://ja.wikipedia.org/wiki/%E6%98%87%E9%99%8D%E6%BC%94%E7%AE%97%E5%AD%90)
  - [角運動量の交換関係からみる固有状態 — 物理とか](https://whyitsso.net/physics/quantum_mechanics/angular_mmnt.html)
  - [2014年度夏学期 量子力学II ノート(浜口, 東大, PDF)](https://www-hep.phys.s.u-tokyo.ac.jp/~hama/lectures/2014_QM_note.pdf)

### 第7-9回:パウリ行列・磁場中スピンの時間発展(Larmor歳差)
- $\{\sigma_i,\sigma_j\}=2\delta_{ij}I$, $[\sigma_i,\sigma_j]=2i\epsilon_{ijk}\sigma_k$ から $[\hat s_i,\hat s_j]=i\hbar\epsilon_{ijk}\hat s_k$。
- 磁場中でスピノルが時間発展し、スピン期待値が角振動数 $\omega=2\mu B/\hbar$ で歳差運動(Larmor歳差)する。
- 出典:
  - [スピンのラーモア歳差運動 — EMANの量子力学](https://eman-physics.net/quantum/larmor_spin.html)
  - [一様な磁場中のスピン状態の時間発展 — 三浦ノート](https://www.k-pmpstudy.com/entry/2018/10/25/spinBdev)

### 第10-12回:摂動論・スピン軌道相互作用・調和振動子
- 非対称な井戸型ポテンシャルへの2次摂動、$\displaystyle\sum_{n=1}^\infty \frac{n^2}{(4n^2-1)^3}$ のような和の利用。
- スピン軌道相互作用 $\hat V_{LS}=\dfrac{e^2}{4\pi\epsilon_0}\dfrac{1}{2m^2c^2}\dfrac1{r^3}\hat{\boldsymbol l}\cdot\hat{\boldsymbol s}$ の2p状態への1次摂動。
- 調和振動子の生成・消滅演算子 $\hat a,\hat a^\dagger$。
- 出典:
  - [8 摂動論(首都大 兵頭, 講義ノート PDF)](https://hyodo.fpark.tmu.ac.jp/class/2024/QM2/QM2_Note12.pdf)
  - [スピン軌道相互作用 — Wikipedia](https://ja.wikipedia.org/wiki/%E3%82%B9%E3%83%94%E3%83%B3%E8%BB%8C%E9%81%93%E7%9B%B8%E4%BA%92%E4%BD%9C%E7%94%A8)
  - [生成演算子と消滅演算子 — EMANの量子力学](https://eman-physics.net/quantum/creat_op.html)
  - [量子力学II講義プリント(加藤, PDF)](https://webpark1378.sakura.ne.jp/kato/qm2note.pdf)
