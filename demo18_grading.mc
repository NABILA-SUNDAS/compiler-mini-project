// simple grading using if/else ladder
start
    int marks = 76;

    if (marks >= 80) {
        print(1);     // grade A
    } else {
        if (marks >= 60) {
            print(2); // grade B
        } else {
            if (marks >= 40) {
                print(3); // grade C
            } else {
                print(4); // fail
            }
        }
    }
end
