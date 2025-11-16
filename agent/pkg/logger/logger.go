package logger

import (
	"fmt"
	"log"
	"os"
	"time"
)

// Level represents log level
type Level int

const (
	DEBUG Level = iota
	INFO
	WARN
	ERROR
)

var (
	currentLevel = INFO
	logger       = log.New(os.Stdout, "", 0)
)

// SetLevel sets the current log level
func SetLevel(level Level) {
	currentLevel = level
}

func formatMessage(level string, format string, v ...interface{}) string {
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	message := fmt.Sprintf(format, v...)
	return fmt.Sprintf("[%s] [%s] %s", timestamp, level, message)
}

// Debug logs a debug message
func Debug(format string, v ...interface{}) {
	if currentLevel <= DEBUG {
		logger.Println(formatMessage("DEBUG", format, v...))
	}
}

// Info logs an info message
func Info(format string, v ...interface{}) {
	if currentLevel <= INFO {
		logger.Println(formatMessage("INFO", format, v...))
	}
}

// Warn logs a warning message
func Warn(format string, v ...interface{}) {
	if currentLevel <= WARN {
		logger.Println(formatMessage("WARN", format, v...))
	}
}

// Error logs an error message
func Error(format string, v ...interface{}) {
	if currentLevel <= ERROR {
		logger.Println(formatMessage("ERROR", format, v...))
	}
}

// Fatal logs a fatal message and exits
func Fatal(format string, v ...interface{}) {
	logger.Println(formatMessage("FATAL", format, v...))
	os.Exit(1)
}

