# Zone Classification Flowchart

## Main Classification Flow
```
START
  ↓
[Input: Density, Speed, Variance]
  ↓
┌─────────────────────────────────┐
│  STEP 1: Density Classification │
└─────────────────────────────────┘
  ↓
  ├─→ Density < 2.0? ──→ BASE: SAFE
  ├─→ 2.0 ≤ Density < 3.5? ──→ BASE: MODERATE
  ├─→ 3.5 ≤ Density < 5.0? ──→ BASE: WARNING
  ├─→ 5.0 ≤ Density < 7.0? ──→ BASE: CRITICAL
  └─→ Density ≥ 7.0? ──→ BASE: EMERGENCY
  ↓
┌─────────────────────────────────┐
│  STEP 2: Calculate Severity     │
│  Score = (D×0.6 + S×0.2 + V×0.2) │
└─────────────────────────────────┘
  ↓
┌─────────────────────────────────┐
│  STEP 3: Movement Adjustment?   │
└─────────────────────────────────┘
  ↓
  ├─→ Speed < 0.5 AND Variance > 120?
  │   ├─→ YES: ELEVATE +1 level (Panic detected)
  │   └─→ NO: Continue
  │
  └─→ Speed > 1.5 AND Variance < 60?
      ├─→ YES: MAINTAIN level (Orderly)
      └─→ NO: Continue
  ↓
┌─────────────────────────────────┐
│  STEP 4: Assign Color & Alert   │
└─────────────────────────────────┘
  ↓
[Output: Level, Color, Severity, Action Flag]
  ↓
END
```

## Detailed Decision Tree
```
                    [Zone Parameters]
                           |
              ┌────────────┴────────────┐
              ↓                         ↓
        [Density Check]           [Movement Check]
              |                         |
    ┌─────────┼─────────┐              |
    ↓         ↓         ↓              ↓
 0-2.0    2.0-3.5   3.5-5.0      [Speed & Variance]
    ↓         ↓         ↓              |
  SAFE   MODERATE   WARNING       ┌────┴────┐
    |         |         |          ↓         ↓
    |         |         |       Panic?   Orderly?
    |         |         |          |         |
    |         |         |       Elevate   Maintain
    |         |         |          |         |
    └─────────┴─────────┴──────────┴─────────┘
                      |
                [Final Classification]
                      |
              ┌───────┴────────┐
              ↓                ↓
         [Color Code]    [Severity Score]
              |                |
         [Alert Level]   [Action Required]
```

## Panic Detection Logic
```
┌─────────────────────────────────┐
│     Panic Indicator Check       │
└─────────────────────────────────┘
              |
    ┌─────────┴─────────┐
    ↓                   ↓
Speed < 0.5?      Variance > 120°?
    |                   |
    YES                 YES
    └─────────┬─────────┘
              ↓
       [BOTH CONDITIONS MET]
              ↓
     ┌────────────────────┐
     │  Elevate +1 Level  │
     │  (Gridlock/Panic)  │
     └────────────────────┘
              ↓
      Moderate → Warning
      Warning → Critical
      Critical → Emergency
```

## Severity Score Calculation
```
┌──────────────────────────────────────┐
│     Severity Score Formula           │
│                                      │
│  Score = (D × 0.6) + (S × 0.2) +    │
│          (V × 0.2)                   │
│                                      │
│  Where:                              │
│  D = (density / 10) × 100            │
│  S = (1 - speed/2) × 100             │
│  V = (variance / 180) × 100          │
│                                      │
│  Result: 0-100                       │
└──────────────────────────────────────┘
```

## Classification Level Matrix
```
┌─────────────┬──────────┬─────────┬──────────┬─────────────┐
│   Density   │  Level   │  Color  │  Alert   │   Action    │
├─────────────┼──────────┼─────────┼──────────┼─────────────┤
│   0 - 2.0   │   SAFE   │  Green  │    0     │     No      │
├─────────────┼──────────┼─────────┼──────────┼─────────────┤
│  2.0 - 3.5  │ MODERATE │ Yellow- │    1     │     No      │
│             │          │  Green  │          │             │
├─────────────┼──────────┼─────────┼──────────┼─────────────┤
│  3.5 - 5.0  │ WARNING  │ Yellow  │    2     │    Yes      │
├─────────────┼──────────┼─────────┼──────────┼─────────────┤
│  5.0 - 7.0  │ CRITICAL │ Orange  │    3     │    Yes      │
├─────────────┼──────────┼─────────┼──────────┼─────────────┤
│    ≥ 7.0    │EMERGENCY │   Red   │    4     │    Yes      │
└─────────────┴──────────┴─────────┴──────────┴─────────────┘
```

---
**Version:** 1.0  
**Last Updated:** January 2026