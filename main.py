import argparse
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .tac import TACGenerator
from .vm import VM
from .errors import LexError, ParseError, SemanticError, RuntimeErrorMC
from .tokens import TokenType

# ====== Simple ANSI Colors ======
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"


def color_ok_fail(count: int) -> str:
    """0 ho to green, warna red."""
    if count == 0:
        return f"{GREEN}{count}{RESET}"
    return f"{RED}{count}{RESET}"


def main():
    ap = argparse.ArgumentParser(description="Mini compiler for simple language")
    ap.add_argument("file", help="source file (.mc)")
    ap.add_argument("--lex", action="store_true", help="show only lexer tokens")
    ap.add_argument(
        "--tac-only",
        dest="tac_only",
        action="store_true",
        help="show only three-address code",
    )
    ap.add_argument(
        "--run",
        action="store_true",
        help="run program after TAC (default: show all phases + run)",
    )
    args = ap.parse_args()

    # flags ka logic
    lex_only = args.lex and not args.tac_only and not args.run
    tac_only = args.tac_only and not args.run
    run_program = args.run or (not args.lex and not args.tac_only)

    # source file read
    with open(args.file, "r") as f:
        source = f.read()

    # ====== Counters / Stats ======
    lex_errors = 0
    parse_errors = 0
    semantic_errors = 0
    runtime_errors = 0

    total_tokens = 0
    unique_lexemes_count = 0
    tac_instr_count = 0
    vm_executed = False

    try:
        # -----------------------------------------------------------
        # 1) LEXER
        # -----------------------------------------------------------
        print(f"{BOLD}{CYAN}--- LEXER (Lexemes / Tokens) ---{RESET}")
        lex = Lexer(source)
        tokens = lex.scan_tokens()

        for t in tokens:
            print(f"{t.lexeme!r}\t=> {t.type.name}")
        print()

        user_tokens = [t for t in tokens if t.type is not TokenType.EOF]
        unique_lexemes = {t.lexeme for t in user_tokens}
        total_tokens = len(user_tokens)
        unique_lexemes_count = len(unique_lexemes)

        print(f"{BOLD}=== LEXER SUMMARY ==={RESET}")
        print(f"TOTAL TOKENS      : {total_tokens}")
        print(f"UNIQUE LEXEMES    : {unique_lexemes_count}")
        print(f"LEXICAL ERRORS    : {color_ok_fail(lex_errors)}")
        print()

        # sirf lexer dekhna hai to yahin tak phases, lekin summary finally mein phir bhi print hogi
        if lex_only:
            return

        # -----------------------------------------------------------
        # 2) PARSER
        # -----------------------------------------------------------
        print(f"{BOLD}{CYAN}--- PARSER (Syntax) ---{RESET}")
        parser = Parser(tokens)
        program = parser.parse()
        print(f"{GREEN}OK: no syntax/parse error{RESET}")
        print(f"SYNTAX ERRORS     : {color_ok_fail(parse_errors)}")
        print()

        # -----------------------------------------------------------
        # 3) SEMANTIC ANALYSIS
        # -----------------------------------------------------------
        print(f"{BOLD}{CYAN}--- SEMANTIC ANALYSIS ---{RESET}")
        sem = SemanticAnalyzer()
        sem.analyze(program)
        print(f"{GREEN}OK: no semantic error{RESET}")
        print(f"SEMANTIC ERRORS   : {color_ok_fail(semantic_errors)}")
        print()

        # -----------------------------------------------------------
        # 4) TAC (Three Address Code)
        # -----------------------------------------------------------
        print(f"{BOLD}{CYAN}--- THREE ADDRESS CODE (ICG) ---{RESET}")
        tac_gen = TACGenerator()
        tac = tac_gen.generate(program)

        if tac:
            # convert to a list to ensure it's iterable/re-iterable and to avoid "not iterable" issues
            try:
                tac_list = list(tac)
                for line in tac_list:
                    print(line)
                tac_instr_count = len(tac_list)
                tac = tac_list
            except TypeError:
                # tac is not iterable -> treat as no TAC produced
                print(f"{YELLOW}[warning]{RESET} No TAC produced (TAC result not iterable)")
                tac = []
                tac_instr_count = 0
        else:
            print(f"{YELLOW}[warning]{RESET} No TAC produced")
            tac = []
            tac_instr_count = 0
        print()

        # sirf TAC tak dekhna ho (without run)
        if tac_only and not run_program:
            return

        # -----------------------------------------------------------
        # 5) VM (Runtime)
        # -----------------------------------------------------------
        if run_program:
            print(f"{BOLD}{CYAN}--- PROGRAM OUTPUT (VM) ---{RESET}")
            vm = VM(program)
            vm.execute(tac)
            vm_executed = True

    # ===============================================================
    # ERROR HANDLING
    # ===============================================================
    except LexError as e:
        lex_errors += 1
        print(f"\n{BOLD}{RED}--- LEXER ERROR ---{RESET}")
        print(e)
        print(f"TOTAL LEXICAL ERRORS : {lex_errors}")

    except ParseError as e:
        parse_errors += 1
        print(f"\n{BOLD}{RED}--- PARSER (Syntax) ERROR ---{RESET}")
        print(e)
        print(f"TOTAL SYNTAX ERRORS  : {parse_errors}")

    except SemanticError as e:
        semantic_errors += 1
        print(f"\n{BOLD}{RED}--- SEMANTIC ANALYSIS ERROR ---{RESET}")
        print(e)
        print(f"TOTAL SEMANTIC ERRORS: {semantic_errors}")

    except RuntimeErrorMC as e:
        runtime_errors += 1
        print(f"\n{BOLD}{RED}--- RUNTIME ERROR ---{RESET}")
        print(e)
        print(f"TOTAL RUNTIME ERRORS : {runtime_errors}")

    finally:
        # ===========================================================
        # OVERALL SUMMARY TABLE
        # ===========================================================
        print()
        print(f"{BOLD}{CYAN}========== OVERALL SUMMARY =========={RESET}")
        print(f"TOTAL TOKENS       : {total_tokens}")
        print(f"UNIQUE LEXEMES     : {unique_lexemes_count}")
        print(f"LEXICAL ERRORS     : {color_ok_fail(lex_errors)}")
        print(f"SYNTAX ERRORS      : {color_ok_fail(parse_errors)}")
        print(f"SEMANTIC ERRORS    : {color_ok_fail(semantic_errors)}")
        print(f"RUNTIME ERRORS     : {color_ok_fail(runtime_errors)}")
        print(f"TAC INSTRUCTIONS   : {tac_instr_count}")
        print(f"VM EXECUTED        : {GREEN if vm_executed else RED}"
              f"{'YES' if vm_executed else 'NO'}{RESET}")
        print(f"{BOLD}{CYAN}====================================={RESET}")
        print()


if __name__ == "__main__":
    main()
