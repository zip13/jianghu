#!/bin/sh
name=$1; subject=$2
echo "Use your image generation tool to create ONE image, then save it as the file out/icons/$name.png in the current directory. Subject: a single RPG inventory item icon of $subject, shown alone, centered, filling about 80% of the canvas, slight three-quarter angle. Style: semi-realistic painterly Chinese wuxia game art like the attached reference (fine textured brushwork, warm muted earthy palette, soft light). Fully transparent background (PNG with real alpha), no frame, no shadow box, no text. Square canvas 1024x1024. After saving, verify the file exists. Do not modify any other files." | timeout 900 codex exec --skip-git-repo-check -s workspace-write -C . -i ref/ENEMY_ART.webp - > "out/icons/$name.log" 2>&1
echo "$name: $(ls out/icons/$name.png 2>&1)"
