#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/20 13:00:00.000000
Revised: 2026/03/25 10:48:27.135252
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ximrato_server.models.lookup import ExerciseCategory
from ximrato_server.models.session import Exercise

_EXERCISES: list[tuple] = [
    # (name, category, equipment_type, name_es, name_gl, primary_muscles, secondary_muscles, description)
    (
        "Bench Press",
        "push",
        "barbell",
        "Press de Banca",
        "Press de Banco",
        ["chest", "front_delts", "triceps"],
        ["biceps"],
        "Barbell press lying on a flat bench. Primary compound exercise for chest development.",
    ),
    (
        "Overhead Press",
        "push",
        "barbell",
        "Press Militar",
        "Press Militar",
        ["front_delts", "triceps"],
        ["side_delts", "traps", "core"],
        "Press a barbell from shoulder height to overhead. Builds front delts and triceps.",
    ),
    (
        "Push-up",
        "push",
        "bodyweight",
        "Flexión",
        "Flexión",
        ["chest", "front_delts", "triceps"],
        ["core"],
        "Lower and raise your body from the floor with arms extended. Classic bodyweight pressing movement.",
    ),
    (
        "Dumbbell Fly",
        "push",
        "dumbbell",
        "Apertura con Mancuernas",
        "Apertura con Mancuernas",
        ["chest"],
        ["front_delts"],
        "Arc dumbbells out and back together while lying on a bench. Chest isolation exercise.",
    ),
    (
        "Tricep Dip",
        "push",
        "bodyweight",
        "Fondos de Tríceps",
        "Fondos de Tríceps",
        ["triceps"],
        ["chest", "front_delts"],
        "Lower and raise your body between parallel bars. Compound tricep exercise.",
    ),
    (
        "Tricep Pushdown",
        "push",
        "cable",
        "Jalón de Tríceps",
        "Extensión de Tríceps",
        ["triceps"],
        [],
        "Push a cable attachment downward to extend the elbow. Isolates the triceps.",
    ),
    (
        "Pull-up",
        "pull",
        "bodyweight",
        "Dominada",
        "Dominada",
        ["lats", "biceps"],
        ["rear_delts", "traps", "core"],
        "Hang from a bar and pull your chin above it. Compound back and bicep exercise.",
    ),
    (
        "Barbell Row",
        "pull",
        "barbell",
        "Remo con Barra",
        "Remo con Barra",
        ["lats", "traps", "rhomboids"],
        ["biceps", "rear_delts", "lower_back"],
        "Hinge at the hips and row a barbell to your lower chest. Builds upper back thickness.",
    ),
    (
        "Dumbbell Row",
        "pull",
        "dumbbell",
        "Remo con Mancuerna",
        "Remo con Mancuerna",
        ["lats", "traps", "rhomboids"],
        ["biceps", "rear_delts"],
        "Row a dumbbell to your hip with one hand braced on a bench. Targets lats and upper back.",
    ),
    (
        "Lat Pulldown",
        "pull",
        "cable",
        "Jalón al Pecho",
        "Jalón ao Peito",
        ["lats", "biceps"],
        ["traps", "rear_delts"],
        "Pull a cable bar down to your upper chest. Machine-based lat exercise.",
    ),
    (
        "Face Pull",
        "pull",
        "cable",
        "Jalón a la Cara",
        "Jalón á Cara",
        ["rear_delts", "traps"],
        ["biceps"],
        "Pull a rope attachment towards your face at ear level. Targets rear delts and upper traps.",
    ),
    (
        "Barbell Curl",
        "pull",
        "barbell",
        "Curl con Barra",
        "Curl con Barra",
        ["biceps"],
        ["forearms"],
        "Curl a barbell from hip level to your chest. Classic bicep exercise.",
    ),
    (
        "Squat",
        "legs",
        "barbell",
        "Sentadilla",
        "Sentadilla",
        ["quads", "glutes"],
        ["hamstrings", "core", "lower_back"],
        "Lower your body with a barbell on your back by bending the knees and hips.",
    ),
    (
        "Deadlift",
        "legs",
        "barbell",
        "Peso Muerto",
        "Peso Morto",
        ["glutes", "hamstrings", "lower_back"],
        ["quads", "traps", "core"],
        "Lift a barbell from the floor to a standing position. Full-body compound exercise.",
    ),
    (
        "Leg Press",
        "legs",
        "machine",
        "Prensa de Piernas",
        "Prensa de Pernas",
        ["quads", "glutes"],
        ["hamstrings"],
        "Press a weight sled upward with your feet on a machine platform.",
    ),
    (
        "Lunge",
        "legs",
        "bodyweight",
        "Zancada",
        "Zancada",
        ["quads", "glutes"],
        ["hamstrings", "core"],
        "Step forward and lower your back knee toward the floor. Unilateral leg exercise.",
    ),
    (
        "Romanian Deadlift",
        "legs",
        "barbell",
        "Peso Muerto Rumano",
        "Peso Morto Rumano",
        ["hamstrings", "glutes"],
        ["lower_back"],
        "Lower a barbell along your legs by hinging at the hips with slight knee bend. Targets hamstrings.",
    ),
    (
        "Leg Curl",
        "legs",
        "machine",
        "Curl Femoral",
        "Curl Femoral",
        ["hamstrings"],
        ["calves"],
        "Curl your legs against resistance on a machine. Isolates the hamstrings.",
    ),
    (
        "Calf Raise",
        "legs",
        "machine",
        "Elevación de Talones",
        "Elevación de Talóns",
        ["calves"],
        [],
        "Rise up on your toes against resistance. Isolates the calf muscles.",
    ),
    (
        "Plank",
        "core",
        "bodyweight",
        "Plancha",
        "Prancha",
        ["core"],
        ["shoulders", "glutes"],
        "Hold a rigid push-up position on your forearms. Core stability exercise.",
    ),
    (
        "Crunch",
        "core",
        "bodyweight",
        "Crunch Abdominal",
        "Crunch Abdominal",
        ["core"],
        ["hip_flexors"],
        "Curl your upper back off the floor toward your knees. Targets the upper abs.",
    ),
    (
        "Russian Twist",
        "core",
        "bodyweight",
        "Giro Ruso",
        "Xiro Ruso",
        ["obliques", "core"],
        ["hip_flexors"],
        "Rotate your torso side to side while seated with feet raised. Works the obliques.",
    ),
    (
        "Leg Raise",
        "core",
        "bodyweight",
        "Elevación de Piernas",
        "Elevación de Pernas",
        ["core", "hip_flexors"],
        ["obliques"],
        "Raise your legs from hanging or lying down. Works lower abs and hip flexors.",
    ),
    (
        "Ab Wheel Rollout",
        "core",
        "ab_wheel",
        "Rueda Abdominal",
        "Roda Abdominal",
        ["core"],
        ["lower_back", "shoulders"],
        "Roll an ab wheel forward from a kneeling position. Demanding core stability exercise.",
    ),
]


def seed_exercises(db: Session) -> None:
    cat_rows = db.execute(select(ExerciseCategory.name, ExerciseCategory.id)).all()
    cat_map: dict[str, int] = {row.name: row.id for row in cat_rows}

    existing_map: dict[str, Exercise] = {ex.name: ex for ex in db.scalars(select(Exercise)).all()}

    for name, category, equipment_type, name_es, name_gl, primary, secondary, description in _EXERCISES:
        ex = existing_map.get(name)
        if ex is None:
            ex = Exercise(name=name)
            db.add(ex)
        ex.category_id = cat_map.get(category)
        ex.equipment_type = equipment_type
        ex.name_es = name_es
        ex.name_gl = name_gl
        ex.primary_muscles = primary
        ex.secondary_muscles = secondary
        ex.description = description

    db.commit()
