#!/usr/bin/env python3
"""
Comprehensive analysis of legal move annotations across all cases.
Runs validation tests defined in VALIDATION_PLAN.txt.
"""

import re, json, os
from collections import Counter, defaultdict
from pathlib import Path

EXPERIMENT_DIR = Path(os.path.expanduser("~/Desktop/legal-moves-experiment"))

KNOWN_MOVES = {
    # Original taxonomy (30)
    "NARROW_STATUTE", "BROADEN_STATUTE", "NARROW_HOLDING", "BROADEN_HOLDING",
    "DISTINGUISH", "ANALOGIZE", "APPLY_STANDARD", "APPLY_TO_FACTS", "BURDEN_SHIFT",
    "INVOKE_AUTHORITY", "DISTINGUISH_PURPOSE", "CONST_AVOIDANCE",
    "CONSTITUTIONAL_AVOIDANCE", "JURISDICTIONAL_REFRAME", "SLIPPERY_SLOPE",
    "ALTERNATIVE_HOLDING", "ALTERNATIVE_HOLDING_ARGUMENT", "STARE_DECISIS_SHIELD",
    "AFFIRMATIVE_FRAME", "CONCEDE_AND_REDIRECT", "CONCEDE_REDIRECT",
    "PREEMPTIVE_REBUTTAL", "ESCALATE_STAKES", "FRAME_AS_ERROR",
    "INSTITUTIONAL_REBUKE", "AGREEMENT_TRAP",
    "FOREGROUND", "BACKGROUND", "RECHARACTERIZE", "SEQUENCE",
    "STRATEGIC_SILENCE", "FOREGROUND_ABSENCE", "DIMINISHING_MODIFIER",
    "OPPONENT_CONCESSION_CAPTURE",
    "COMPRESSION", "CADENCE_SHIFT", "CONCRETE_ANCHOR",
    "UNDERSTATED_DEVASTATION", "STRATEGIC_QUOTATION",
    "RHETORICAL_QUESTION", "PARALLEL_STRUCTURE", "REGISTER_CONTRAST",
    "AUTHORITY_SIGNALING",
    # Discovered moves
    "ACCUMULATION_OVERWHELM", "STRATEGIC_NON_ENGAGEMENT",
    "SILENCE_AS_CONCESSION", "DILEMMA_CONSTRUCTION",
    "STRATEGIC_SHIFT_EXPOSURE", "SUPERFLUITY_ARGUMENT",
    "PROCESS_LEGITIMATION", "WAIVER_TRAP", "REDUCTIO_BY_EXAMPLE",
    "SELF_REFUTING_DEFENSE", "STRAW_MAN_EXPOSURE",
    "AUTHORITY_INVERSION", "APPELLATE_POSITION_REVERSAL",
    "INTRA_STATUTORY_CONTRAST",
}

LAYERS = ["DOCTRINAL", "NARRATIVE", "FACT-FRAMING", "STYLISTIC"]

LAYER_MOVES = {
    "DOCTRINAL": {"NARROW_STATUTE", "BROADEN_STATUTE", "NARROW_HOLDING", "BROADEN_HOLDING",
        "DISTINGUISH", "ANALOGIZE", "APPLY_STANDARD", "APPLY_TO_FACTS", "BURDEN_SHIFT",
        "INVOKE_AUTHORITY", "DISTINGUISH_PURPOSE", "CONST_AVOIDANCE", "CONSTITUTIONAL_AVOIDANCE",
        "JURISDICTIONAL_REFRAME", "SLIPPERY_SLOPE", "ALTERNATIVE_HOLDING",
        "ALTERNATIVE_HOLDING_ARGUMENT", "STARE_DECISIS_SHIELD", "SUPERFLUITY_ARGUMENT",
        "INTRA_STATUTORY_CONTRAST", "STRAW_MAN_EXPOSURE", "REDUCTIO_BY_EXAMPLE"},
    "NARRATIVE": {"AFFIRMATIVE_FRAME", "CONCEDE_AND_REDIRECT", "CONCEDE_REDIRECT",
        "PREEMPTIVE_REBUTTAL", "ESCALATE_STAKES", "FRAME_AS_ERROR",
        "INSTITUTIONAL_REBUKE", "AGREEMENT_TRAP", "DILEMMA_CONSTRUCTION",
        "STRATEGIC_SHIFT_EXPOSURE", "STRATEGIC_NON_ENGAGEMENT",
        "APPELLATE_POSITION_REVERSAL", "WAIVER_TRAP", "SELF_REFUTING_DEFENSE"},
    "FACT-FRAMING": {"FOREGROUND", "BACKGROUND", "RECHARACTERIZE", "SEQUENCE",
        "STRATEGIC_SILENCE", "FOREGROUND_ABSENCE", "DIMINISHING_MODIFIER",
        "OPPONENT_CONCESSION_CAPTURE", "SILENCE_AS_CONCESSION",
        "PROCESS_LEGITIMATION", "ACCUMULATION_OVERWHELM"},
    "STYLISTIC": {"COMPRESSION", "CADENCE_SHIFT", "CONCRETE_ANCHOR",
        "UNDERSTATED_DEVASTATION", "STRATEGIC_QUOTATION",
        "RHETORICAL_QUESTION", "PARALLEL_STRUCTURE", "REGISTER_CONTRAST",
        "AUTHORITY_SIGNALING", "AUTHORITY_INVERSION"},
}


def parse_annotation_file(filepath):
    """Parse a single annotation file and extract structured data."""
    with open(filepath) as f:
        content = f.read()

    # Find argument units with multiple patterns
    au_patterns = [
        r'ARGUMENT UNIT \S+',
        r'--- AU-[A-Z0-9]+\.\d+ ---',
        r'AU [A-Z]-[IVX]+-\d+',
    ]
    
    au_starts = []
    for pat in au_patterns:
        au_starts.extend((m.start(), m.group()) for m in re.finditer(pat, content))
    au_starts.sort(key=lambda x: x[0])
    
    # Deduplicate overlapping matches
    deduped = []
    for start, label in au_starts:
        if not deduped or start > deduped[-1][0] + 50:
            deduped.append((start, label))
    au_starts = deduped

    results = {
        "au_count": len(au_starts),
        "layer_filled": Counter(),
        "layer_empty": Counter(),
        "moves_per_layer": defaultdict(list),
        "all_moves": [],
        "new_moves": [],
        "cross_brief_interactions": 0,
    }

    # Count cross-brief interactions
    results["cross_brief_interactions"] = len(re.findall(
        r'CROSS-BRIEF|Cross-Brief Interaction', content, re.IGNORECASE))

    for i, (start, label) in enumerate(au_starts):
        end = au_starts[i+1][0] if i+1 < len(au_starts) else len(content)
        block = content[start:end]

        for layer in LAYERS:
            pattern = rf'{layer}:\s*(.*?)(?=\n\s*(?:DOCTRINAL|NARRATIVE|FACT-FRAMING|STYLISTIC|ARGUMENT UNIT|--- AU|CROSS-BRIEF|AU [A-Z]|\n\n\n|$))'
            match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
            if match:
                annotation = match.group(1).strip()
                if annotation.startswith("--") or annotation == "" or annotation == "N/A":
                    results["layer_empty"][layer] += 1
                else:
                    results["layer_filled"][layer] += 1
                    words = re.findall(r'[A-Z][A-Z_]{2,}', annotation)
                    for w in words:
                        if w in KNOWN_MOVES:
                            results["moves_per_layer"][layer].append(w)
                            results["all_moves"].append(w)

    # Find new moves
    new_found = re.findall(r'NEW_MOVE_\[([A-Z_]+)\]', content)
    results["new_moves"] = list(set(new_found))

    return results


def run_analysis():
    # Find all annotation files
    annotation_files = sorted(EXPERIMENT_DIR.glob("annotations_*.txt"))
    print(f"Found {len(annotation_files)} annotation files\n")

    all_case_data = {}
    global_moves = Counter()
    global_layer_filled = Counter()
    global_layer_empty = Counter()
    global_moves_per_layer = defaultdict(Counter)
    total_aus = 0
    convergence = []

    for filepath in annotation_files:
        docket = filepath.stem.replace("annotations_", "")
        data = parse_annotation_file(filepath)
        all_case_data[docket] = data
        total_aus += data["au_count"]

        move_counts = Counter(data["all_moves"])
        global_moves.update(move_counts)

        for layer in LAYERS:
            global_layer_filled[layer] += data["layer_filled"].get(layer, 0)
            global_layer_empty[layer] += data["layer_empty"].get(layer, 0)
            for move in data["moves_per_layer"].get(layer, []):
                global_moves_per_layer[layer][move] += 1

        convergence.append((docket, len(data["new_moves"])))

    # ===== REPORT =====
    print("=" * 70)
    print(f"COMPREHENSIVE ANALYSIS — {len(annotation_files)} CASES, {total_aus} ARGUMENT UNITS")
    print("=" * 70)

    # 1. LAYER COVERAGE
    print(f"\n{'='*70}")
    print("1. LAYER COVERAGE")
    print(f"{'='*70}\n")
    for layer in LAYERS:
        filled = global_layer_filled[layer]
        empty = global_layer_empty[layer]
        total = filled + empty
        pct = (filled / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {layer:15s}: {bar} {pct:5.1f}% ({filled}/{total})")

    # 2. MOVE FREQUENCY
    print(f"\n{'='*70}")
    print("2. MOVE FREQUENCY DISTRIBUTION")
    print(f"{'='*70}\n")
    total_apps = sum(global_moves.values())
    print(f"  Total move applications: {total_apps}")
    print(f"  Unique moves used: {len(global_moves)}\n")
    
    for rank, (move, count) in enumerate(global_moves.most_common(20), 1):
        pct = count / total_apps * 100
        bar = "■" * min(count, 40)
        print(f"  {rank:2d}. {move:35s} {count:3d} ({pct:4.1f}%) {bar}")
    
    if len(global_moves) > 20:
        remaining = global_moves.most_common()[20:]
        print(f"\n  ... plus {len(remaining)} more moves with counts: ", end="")
        print(", ".join(f"{m}({c})" for m, c in remaining[:10]))

    # 3. MOVES BY LAYER
    print(f"\n{'='*70}")
    print("3. TOP MOVES PER LAYER")
    print(f"{'='*70}")
    for layer in LAYERS:
        layer_counts = global_moves_per_layer[layer]
        print(f"\n  {layer}:")
        for move, count in layer_counts.most_common(8):
            print(f"    {move:35s} {count:3d}")

    # 4. CONVERGENCE
    print(f"\n{'='*70}")
    print("4. TAXONOMY CONVERGENCE")
    print(f"{'='*70}\n")
    cumulative = 0
    for i, (docket, n) in enumerate(convergence):
        cumulative += n
        marker = "✓" if n == 0 else " "
        print(f"  Case {i+1:2d} ({docket:>8s}): {marker} {n} new  (cumulative: {cumulative})")
    
    zero_cases = sum(1 for _, n in convergence if n == 0)
    print(f"\n  Zero-new cases: {zero_cases}/{len(convergence)} ({zero_cases/len(convergence)*100:.0f}%)")
    if len(convergence) >= 6:
        last6 = convergence[-6:]
        print(f"  Last 6 avg: {sum(n for _,n in last6)/6:.1f} new/case")

    # 5. CROSS-CASE CONSISTENCY
    print(f"\n{'='*70}")
    print("5. CROSS-CASE CONSISTENCY")
    print(f"{'='*70}\n")
    
    # Which moves appear in the most cases?
    move_case_presence = defaultdict(set)
    for docket, data in all_case_data.items():
        for move in set(data["all_moves"]):
            move_case_presence[move].add(docket)
    
    print("  Moves appearing in most cases:")
    for move, cases_set in sorted(move_case_presence.items(), key=lambda x: -len(x[1]))[:15]:
        pct = len(cases_set) / len(all_case_data) * 100
        print(f"    {move:35s} {len(cases_set):2d}/{len(all_case_data)} cases ({pct:.0f}%)")
    
    # Moves appearing in only 1 case
    singleton_moves = [m for m, s in move_case_presence.items() if len(s) == 1]
    print(f"\n  Singleton moves (1 case only): {len(singleton_moves)}")
    for m in sorted(singleton_moves):
        print(f"    {m}")

    # 6. POWER LAW TEST
    print(f"\n{'='*70}")
    print("6. DISTRIBUTION SHAPE")
    print(f"{'='*70}\n")
    counts = sorted(global_moves.values(), reverse=True)
    top5_share = sum(counts[:5]) / sum(counts) * 100
    top10_share = sum(counts[:10]) / sum(counts) * 100
    bottom_half_share = sum(counts[len(counts)//2:]) / sum(counts) * 100
    print(f"  Top 5 moves:  {top5_share:.1f}% of all applications")
    print(f"  Top 10 moves: {top10_share:.1f}% of all applications")
    print(f"  Bottom half:  {bottom_half_share:.1f}% of all applications")
    print(f"  Gini-like concentration: {'HIGH' if top5_share > 30 else 'MODERATE' if top5_share > 20 else 'LOW'}")

    return all_case_data, global_moves


if __name__ == "__main__":
    run_analysis()
