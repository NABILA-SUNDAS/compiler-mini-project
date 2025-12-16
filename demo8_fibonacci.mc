// first 7 terms of fibonacci series
start
    int n1 = 0;
    int n2 = 1;
    int n3 = 0;
    int i = 0;

    print(n1);
    print(n2);

    while (i < 5) {
        n3 = n1 + n2;
        print(n3);
        n1 = n2;
        n2 = n3;
        i = i + 1;
    }
end
