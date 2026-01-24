#!/bin/bash
# Скрипт для быстрого переключения между моделями Claude
# Использование: ./switch-claude-model.sh [haiku|sonnet|sonnet45]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_FILE="$SCRIPT_DIR/.env"
ENV_EXAMPLE_FILE="$SCRIPT_DIR/env.example"

# Определяем модель по параметру
MODEL=${1:-sonnet45}

case $MODEL in
    haiku)
        SELECTED_MODEL="claude-3-haiku-20240307"
        ;;
    sonnet)
        SELECTED_MODEL="claude-3-5-sonnet-20241022"
        ;;
    sonnet45)
        SELECTED_MODEL="claude-sonnet-4-5-20250929"
        ;;
    *)
        echo "❌ Неверный параметр: $MODEL"
        echo "Использование: $0 [haiku|sonnet|sonnet45]"
        exit 1
        ;;
esac

echo ""
echo "🔄 Переключение модели Claude..."
echo "   Выбранная модель: $SELECTED_MODEL"

if [ ! -f "$ENV_FILE" ]; then
    echo ""
    echo "⚠️  Файл .env не найден, создаю из env.example..."
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    else
        echo "❌ Файл env.example также не найден!"
        exit 1
    fi
fi

# Обновляем или добавляем CLAUDE_MODEL
if grep -q "CLAUDE_MODEL=" "$ENV_FILE"; then
    # Обновляем существующую переменную
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/CLAUDE_MODEL=.*/CLAUDE_MODEL=$SELECTED_MODEL/" "$ENV_FILE"
    else
        # Linux
        sed -i "s/CLAUDE_MODEL=.*/CLAUDE_MODEL=$SELECTED_MODEL/" "$ENV_FILE"
    fi
    echo "   ✅ Обновлена существующая переменная CLAUDE_MODEL"
else
    # Добавляем новую переменную
    echo "" >> "$ENV_FILE"
    echo "# Claude Model Selection" >> "$ENV_FILE"
    echo "CLAUDE_MODEL=$SELECTED_MODEL" >> "$ENV_FILE"
    echo "   ✅ Добавлена новая переменная CLAUDE_MODEL"
fi

echo ""
echo "✅ Модель успешно переключена на: $SELECTED_MODEL"
echo ""
echo "📋 Информация о моделях:"
echo "   haiku    - Claude 3 Haiku (legacy) - ~\$0.80/\$4 за млн токенов"
echo "   sonnet   - Claude 3.5 Sonnet - ~\$3/\$15 за млн токенов"
echo "   sonnet45 - Claude 4.5 Sonnet - ~\$3/\$15 за млн токенов (самая умная)"
echo ""
echo "⚠️  ВАЖНО: Перезапустите backend для применения изменений!"
echo "   Команда: cd backend && npm run dev"
echo ""



