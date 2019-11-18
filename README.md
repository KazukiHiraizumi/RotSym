# The estimation method of the symmetry axis in point clouds

## 目的

回転対称物体の認識にてソルバーは必ずしも最小の回転を算出しない。回転対称物体での回転の最小化は後処理が必要である。

## 回転対称物体の特徴不変座標系  
![fig1](fig1.png)
### 特徴不変座標系の定義  
- 2つ以上の異なる座標系x<sub>i</sub>から観測した物体Mの特徴点が一致するとき、座標系x<sub>i</sub>を物体Mの特徴不変座標系という  
### 定理  
- N相対称の物体は、少なくともN個の特徴不変座標系を持つ

### 特徴不変座標系の求め方  
N相対称の物体Mがある。最初に座標系x<sub>0</sub>として、物体Mの重心を通る座標系wを与える。これにより座標系x<sub>0</sub>(w)は、物体Mの回転軸に近いと仮回転軸と考えて良い。

1. 不変座標系  
x<sub>0</sub>を基準とした不変座標系x<sub>i</sub>への変換行列は以下のように表される  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>x0</sup>T<sub>xi</sub>  
この変換にて物体Mをx<sub>0</sub>座標系上で移動させると以下となる  
&nbsp;&nbsp;&nbsp;&nbsp;M<sub>xi</sub>=<sup>x0</sup>T<sub>xi</sub>M

2. 仮回転座標系  
座標系x<sub>0</sub>(w)を原点周りに第i相回転させた座標系をw<sub>i</sub>とする。w<sub>i</sub>は仮の回転軸で回転となる。x<sub>0</sub>基準とした変換は以下のよう表される。  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>x0</sup>T<sub>wi</sub>
またこの変換により、物体Mは以下のように移動させる  
&nbsp;&nbsp;&nbsp;&nbsp;M<sub>wi</sub>=<sup>x0</sup>T<sub>wi</sub>M

3. ICP変換  
w<sub>i</sub>は仮の回転軸であるため、Futures(M<sub>wi</sub>)とFutures(M<sub>xi</sub>)は一致しないが、近いところにあるのでICPなどで、差を求めることが出来る。
また、Futures(M<sub>xi</sub>)=Futures(M)のため、M<sub>wi</sub>とM( or Mの0相回転)でICPを行えば良い。これにより  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>x0</sup>T<sub>icp</sub>  
が得られたとする。これより下式を得る。  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>x0</sup>T<sub>xi</sub>M=<sup>x0</sup>T<sub>icp</sub><sup>x0</sup>T<sub>wi</sub>M
or  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>x0</sup>T<sub>xi</sub>=<sup>x0</sup>T<sub>icp</sub><sup>x0</sup>T<sub>wi</sub>

### 固有不変座標系
![fig2](fig2.png)  
前述の手順にて得られた特徴不変座標系は、x<sub>0</sub>を重心を通る座標系として与えたので、必ずしも物体Mの対称軸には一致せず、またそれぞれの原点も異なる(上図左)。不変座標系のうち
<ul>
<li>その原点が全て同一
<li>回転軸が同一
</ul>
であるものを固有不変座標系と呼ぶ(上図右)。「回転軸が同一」の条件は、例えば回転軸を座標系のZ軸とすれば、該座標系の全てのZ基底ベクトルが同一と言い換えられる。

### 固有不変座標系の求め方  
不変座標系x<sub>i</sub>から、固有不変座標系は容易に求められる。簡単のためZ軸を対称軸として手順を示す
<ul>
<li>第0不変座標系x<sub>0</sub>のZ軸を、全ての不変座標系x<sub>i</sub>のZ基底ベクトル和と同じ向きに回転させる
<li>第0不変座標系x<sub>0</sub>の原点を、全ての不変座標系x<sub>i</sub>の原点の重心に移動させる
</ul>
これによって得られた、新たな第0不変座標系x<sub>0</sub>を元に、不変座標系x<sub>i</sub>を求める。  
これを必要な精度が得られるまで、繰り返してもよい。

### 基準座標系の変更  
![fig3](fig3.png)  
以上、物体基準にて不変座標系を求めたが、実用上は原点は自由に定めたい。例えばカメラ座標系を基準にするなどである。上図のようにs座標系を基準とするには  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>s</sup>T<sub>si</sub>=<sup>s</sup>T<sub>x0</sub><sup>x0</sup>T<sub>xi</sub><sup>xi</sup>T<sub>si</sub>  
にてs座標系基準にてN個の不変座標系s<sub>i</sub>に展開できる。  
上式で、<sup>xi</sup>T<sub>si</sub>は不変座標系の定義より  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>si</sup>T<sub>xi</sub>=<sup>s</sup>T<sub>x0</sub>  
であるので、整理すると  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>s</sup>T<sub>si</sub>=<sup>s</sup>T<sub>x0</sub><sup>x0</sup>T<sub>xi</sub><sup>x0</sup>T<sub>s</sub>  

## テストコード  
サンプルデータsurface.plyは3相対称な点群データである。座標系はカメラ座標系を基準としている。  
test.pyは上記手順にて<sup>s</sup>T<sub>si</sub>を求め、これにより元の点群データから120度240度回転の点群データを作り、元のデータを合わせ３セットの点群を重ね描きしている。

## 解析結果の加工  
<sup>s</sup>T<sub>si</sub>が得られれば、解析結果<sup>c</sup>T<sub>s</sub>に対して、不変座標系展開も容易である  
&nbsp;&nbsp;&nbsp;&nbsp;<sup>c</sup>T<sub>si</sub>=<sup>c</sup>T<sub>s</sub><sup>s</sup>T<sub>si</sub>  
<sup>c</sup>T<sub>si</sub>の回転部分の回転量が最小のものを選ぶ。
