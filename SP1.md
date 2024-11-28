
# SP1

**2019-07-14 21:00:45**
    
# TEST - Life, the Universe, and Everything

## 题面翻译

您的程序应该使用暴力破解方法来找到生命、宇宙和一切的答案。更精确地说……将输入的小数字重写到输出中。在读取到数字 $42$ 后停止处理输入。所有输入的数字都是一位或两位的整数。

翻译者：[jiangyunuo](https://www.luogu.com.cn/user/1061050)。

## 题目描述

Your program is to use the brute-force approach in order to _find the Answer to Life, the Universe, and Everything._ More precisely... rewrite small numbers from input to output. Stop processing input after reading in the number 42. All numbers at input are integers of one or two digits.

## 输入格式

## 输出格式

## 样例 #1

### 样例输入 #1

```
1
2
88
42
99
```

### 样例输出 #1

```
1
2
88
```

## 提示

Information
-----------

In case of any problems with your code, you can take a look in the [forum](http://www.spoj.com/forum/), you'll find the answer, only for this problem, in various languages.

# GCX的AC代码
```cpp
#include<cstdio>
int main(){
    int N;
    while(1){
        scanf("%d", &N);
        if(N == 42)
            return 0;
        else
printf("%d\n", N);
    }
}
```

