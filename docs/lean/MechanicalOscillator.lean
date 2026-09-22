/-
  Mechanical Damped Oscillator
  m·ẍ + c·ẋ + k·x = F(t)

  A mass-spring-damper system is one of the canonical examples of a
  second-order linear dynamical system. It appears in:
  - Suspension systems
  - Seismic isolation
  - Vibration control

  Source: Classical mechanics, Newtonian dynamics
  Historical: Analyzed systematically from Newton's Principia onward
-/

import Mathlib.Data.Real.Basic
import Mathlib.LinearAlgebra.Matrix.Basic
import DynamicalSystem

namespace MechanicalOscillator

/- Physical parameters of a damped oscillator -/
structure Parameters where
  m : ℝ      -- Mass (kg)
  c : ℝ      -- Damping coefficient (N·s/m)
  k : ℝ      -- Spring stiffness (N/m)

  -- Physical constraints
  m_pos : m > 0
  c_nonneg : c ≥ 0
  k_pos : k > 0

/- Normalized parameters: natural frequency and damping ratio -/
def getNormalizedForm (p : Parameters) : DynamicalSystem.NormalizedSecondOrder :=
  let ω₀_sq : ℝ := p.k / p.m
  let ζ : ℝ := p.c / (2 * Real.sqrt (p.k * p.m))
  ⟨ω₀_sq, ζ, by
    -- ω₀² > 0 because k > 0 and m > 0
    positivity,
  -- ζ ≥ 0 because c ≥ 0
  by positivity⟩

/- State-space representation
   State: x = [position, velocity]ᵀ

   ẋ₁ = x₂  (velocity is derivative of position)
   ẋ₂ = -(k/m)·x₁ - (c/m)·x₂ + (1/m)·F  (Newton's second law)

   Output: y = x₁  (we measure position)
-/
def toStateSpace (p : Parameters) : DynamicalSystem.LinearTI 2 1 1 :=
  let A : Matrix (Fin 2) (Fin 2) ℝ := fun i j =>
    if i = 0 ∧ j = 1 then 1                    -- ẋ₁ = x₂
    else if i = 1 ∧ j = 0 then -(p.k / p.m)   -- ẋ₂ = -(k/m)·x₁
    else if i = 1 ∧ j = 1 then -(p.c / p.m)   -- -(c/m)·x₂
    else 0
  let B : Matrix (Fin 2) (Fin 1) ℝ := fun i j =>
    if i = 1 then (1 / p.m) else 0             -- F only affects ẋ₂
  let C : Matrix (Fin 1) (Fin 2) ℝ := fun i j =>
    if i = 0 ∧ j = 0 then 1 else 0            -- y = x₁
  let D : Matrix (Fin 1) (Fin 1) ℝ := fun i j => 0  -- No feedthrough
  ⟨A, B, C, D⟩

/- Energy stored in a damped oscillator -/
def kineticEnergy (p : Parameters) (v : ℝ) : ℝ :=
  (1/2) * p.m * v^2

def potentialEnergy (p : Parameters) (x : ℝ) : ℝ :=
  (1/2) * p.k * x^2

def totalEnergy (p : Parameters) (x v : ℝ) : ℝ :=
  potentialEnergy p x + kineticEnergy p v

/- Power dissipated by damping
   P = c·v² (energy lost to friction)
-/
def dissipatedPower (p : Parameters) (v : ℝ) : ℝ :=
  p.c * v^2

end MechanicalOscillator
