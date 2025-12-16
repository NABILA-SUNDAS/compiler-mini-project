// swap two variables without third variable
start
    int a = 5;
    int b = 9;

    print(a);
    print(b);

    a = a + b;
    b = a - b;
    a = a - b;

    print(a);
    print(b);
end
