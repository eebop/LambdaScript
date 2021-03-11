# LAMBDASCRIPT
## DOCUMENTATION
LambdaScript is a lambda-oriented language. In fact, there are *no* functions.
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

### CLASSES
Classes are hard because there is no built-in class type.
However, lambdas can have global variables...
Global variables can be signified with a leading `@`
```
>> OneOffObject = {@data = d}[d]
>> OneOffObject (4)
>> OneOffObject.data
4
>> OneOffObject ('e')
>> OneOffObject.data
'e'
```
You *can* create classes, but you have to make a lambda that returns the objects.
```
>> MyClass = {{@data = d}[d]}
>> MyObject1 = MyClass ()
>> MyObject2 = MyClass ()
>> MyObject1(4092)
>> MyObject2('K')
>> MyObject2.data
'K'
>> MyObject1.data
4092
>> MyObject1.data = 3
>> MyObject1.data
3
>> MyObject1.NotYetCreatedVar = 'alpha'
>> MyObject1.NotYetCreatedVar
'alpha'
>> MyObject2
lambda = { @data = d } ['d']
>> MyObject2.data
'K'
```
Note: __No__ initializing work is done for you. You'll have to build that into the class
Of course, objects can have functions, but you'll have to explicitly pass the `self` value.
