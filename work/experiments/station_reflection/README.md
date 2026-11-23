# Local workstation reflection trial — not adopted

The default game has no hook to this experiment. The original active gameplay script has been restored. Saved gameplay.gd here contains the two-line hook and station_reflection.gd contains the prototype.

Trial 1 affected the ground with a visible lighting region. Trial 2 restricted reflection to the counter and removed that region. Both actual Godot 4.6.3 Forward+ runs logged seven leaked Texture RIDs at shutdown. The close metal grain also needs lower normal strength to avoid a patterned look. Do not enable this as accepted production lighting.

Images/logs: Godot verification_r18/reflection_trial and reflection_trial2; work/audit/r18_reflection_trial*.log. The captures have no script errors, but the shutdown warnings remain unresolved. Default R18 screenshots, movie and performance use the original sky reflection path, not this prototype.
