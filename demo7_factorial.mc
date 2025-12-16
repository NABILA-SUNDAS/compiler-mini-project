// factorial of 5 using loop
start
    int n = 5;
    int fact = 1;
    int i = 1;

    while (i <= n) {
        fact = fact * i;
        i = i + 1;
    }

    print(fact);
end
