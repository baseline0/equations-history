/-
  RLC Circuit (Series)
  L·q̈ + R·q̇ + (1/C)·q = V(t)

  A resistor-inductor-capacitor circuit is the electrical analog of
  a mechanical damped oscillator. The correspondence is so precise that
  solutions to one directly inform the other.

  Domain analogy:
  - Charge ↔ Position
  - Current ↔ Velocity
  - Inductance ↔ Mass
  - Resistance ↔ Damping
  - Capacitance inverse ↔ Stiffness

  Source: Kirchhoff's laws and circuit theory
  Historical: Recognized as analogous to mechanical systems in early 20th century
-/

import Mathlib.Data.Real.Basic
import Mathlib.LinearAlgebra.Matrix.Basic
import DynamicalSystem

namespace RLCCircuit

/- Physical parameters of an RLC circuit -/
structure Parameters where
  L : ℝ      -- Inductance (H)
  R : ℝ      -- Resistance (Ω)
  C : ℝ      -- Capacitance (F)

  -- Physical constraints
  L_pos : L > 0
  R_nonneg : R ≥ 0
  C_pos : C > 0

/- Normalized parameters: natural frequency and damping ratio -/
def getNormalizedForm (p : Parameters) : DynamicalSystem.NormalizedSecondOrder :=
  let ω₀_sq : ℝ := 1 / (L * C)
  let ζ : ℝ := R * Real.sqrt (C / L) / 2
  ⟨ω₀_sq, ζ, by
    -- ω₀² > 0 because L > 0 and C > 0
    positivity,
  -- ζ ≥ 0 because R ≥ 0
  by positivity⟩

/- State-space representation
   State: x = [charge, current]ᵀ

   ẋ₁ = x₂  (current is derivative of charge)
   ẋ₂ = -(1/LC)·x₁ - (R/L)·x₂ + (1/L)·V  (Kirchhoff's voltage law)

   Output: y = x₁  (we measure charge or voltage across capacitor)
-/
def toStateSpace (p : Parameters) : DynamicalSystem.LinearTI 2 1 1 :=
  let A : Matrix (Fin 2) (Fin 2) ℝ := fun i j =>
    if i = 0 ∧ j = 1 then 1                         -- ẋ₁ = x₂
    else if i = 1 ∧ j = 0 then -(1 / (p.L * p.C))  -- ẋ₂ = -(1/LC)·x₁
    else if i = 1 ∧ j = 1 then -(p.R / p.L)        -- -(R/L)·x₂
    else 0
  let B : Matrix (Fin 2) (Fin 1) ℝ := fun i j =>
    if i = 1 then (1 / p.L) else 0                 -- V only affects ẋ₂
  let C : Matrix (Fin 1) (Fin 2) ℝ := fun i j =>
    if i = 0 ∧ j = 0 then 1 else 0                -- y = x₁ (charge)
  let D : Matrix (Fin 1) (Fin 1) ℝ := fun i j => 0  -- No feedthrough
  ⟨A, B, C, D⟩

/- Energy stored in an RLC circuit -/
def magneticEnergy (p : Parameters) (i : ℝ) : ℝ :=
  (1/2) * p.L * i^2

def electricEnergy (p : Parameters) (q : ℝ) : ℝ :=
  (1/2) * (1 / p.C) * q^2

def totalEnergy (p : Parameters) (q i : ℝ) : ℝ :=
  electricEnergy p q + magneticEnergy p i

/- Power dissipated in the resistor
   P = R·i² (energy lost to heat)
-/
def dissipatedPower (p : Parameters) (i : ℝ) : ℝ :=
  p.R * i^2

end RLCCircuit
