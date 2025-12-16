// demo of declarations, loops, if/else, print
start
    int a = 3;
    float b = 2.5;
    int i = 0;

    while (i < 5) {
        a = a + i;
        if (a > 6) {
            print(a);
        } else {
            print(a + b);
        }
        i = i + 1;
    }

    print(a);    // final
end
