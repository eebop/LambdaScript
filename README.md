# LAMBDASCRIPT
## DOCUMENTATION
LambdaScript is a lambda-oriented language. In fact, there are *no* functions or classes.
There are only anonymous lambdas. Apart from that, it works like you might expect.
```
>> 1 + 2
3
>> 2 ^ 4
16
>> "e" + "i"
'ei'
>> 'alpha' + 'beta' + 'gamma' + 'delta'
'alphabetagammadelta'
>> x = 1
>> x
1
>> x + x
2
>> y = 3
>> z := "e'"
"e'"
>> a = b := 3
>> a = b := 3
>> a
3
>> b
3
>> y
3
>> #comment
>> y + x
4
>> print('e')
e>>
```

### CONDITIONALS AND WHILE LOOPS
Conditionals will either return one value or another, depending on whether a third is non-zero.
```
>> if {0} then {1} else {2}
2
>> if {1} then {1} else {2}
1
```
While loops will evaluate one section while another is non-zero.
```
>> while {l} do {print(l);print('\n');l = l-1}
10.0
9.0
8.0
7.0
6.0
5.0
4.0
3.0
2.0
1.0
```

### LAMBDAS
Lambdas are pieces of code that can be executed multiple times.
```
>> ReturnThree = {3}
>> ReturnThree
lambda = { 3 } []
>> ReturnThree ()
3
>> ReturnThree ()
3
```
They can have arguments.
```
>> square = {n * n}[n]
>> square(5)
25
>> square(100)
10000
```
They can be nested.
```
>> returnLambda = {{n * n}[n]}
>> returnLambda ()
lambda = { n * n } ['n']
>> returnLambda
lambda = { { n * n } [ n ] } []
>> returnLambda () (3)
9
```
They can recurse
```
>> factorial = {if {x == 1} then {1} else {factorial(x-1) * x}}[x]
>> factorial(3)
6
>> factorial(4)
24
```
