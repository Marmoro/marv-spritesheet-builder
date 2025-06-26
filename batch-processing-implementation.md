# Batch Processing Implementation Plan

## Overview
This document outlines the implementation details for improving the batch processing in `main-batched.js`. The goal is to enhance performance through concurrent processing while maintaining stability and improving error handling.

## Implementation Details

### 1. Concurrent Processing with Controlled Batching

We'll modify the `processTasks` function to:
- Process multiple sprite sheets concurrently using Promise-based batching
- Control the concurrency to prevent memory issues (5-8 tasks at a time)
- Track progress and provide better reporting

### 2. Code Changes

```javascript
// New utility function to process tasks in batches
async function processBatch(tasks, startIndex, batchSize, totalTasks) {
  const endIndex = Math.min(startIndex + batchSize, tasks.length);
  const batch = tasks.slice(startIndex, endIndex);
  
  const batchPromises = batch.map(async (task, index) => {
    const taskIndex = startIndex + index;
    console.log(`[${taskIndex + 1}/${totalTasks}] Processing: ${path.basename(task.output)}`);
    
    try {
      const result = await spritesmithRun({
        src: task.inputs,
        padding: 0
      });
      
      fs.writeFileSync(task.output, result.image);
      console.log(`✓ Created: ${task.output}`);
      return { success: true, task };
    } catch (error) {
      console.error(`✗ Error processing ${task.output}:`, error);
      return { success: false, task, error };
    }
  });
  
  return Promise.all(batchPromises);
}

// Main processing function with batching
async function processTasks() {
  try {
    // Read the task file
    const tasksData = fs.readFileSync(taskFilePath, 'utf8');
    const tasks = JSON.parse(tasksData);
    
    console.log(`Processing ${tasks.length} sprite sheets`);
    
    // Define batch size and track results
    const BATCH_SIZE = 6; // Process 6 tasks concurrently
    const results = {
      successful: 0,
      failed: 0,
      failedTasks: []
    };
    
    // Process in batches
    for (let i = 0; i < tasks.length; i += BATCH_SIZE) {
      console.log(`\nProcessing batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(tasks.length / BATCH_SIZE)}`);
      
      const batchResults = await processBatch(tasks, i, BATCH_SIZE, tasks.length);
      
      // Update statistics
      batchResults.forEach(result => {
        if (result.success) {
          results.successful++;
        } else {
          results.failed++;
          results.failedTasks.push({
            output: result.task.output,
            error: result.error.message
          });
        }
      });
      
      // Report progress
      const completedPercentage = Math.round(((i + batchResults.length) / tasks.length) * 100);
      console.log(`Progress: ${completedPercentage}% (${i + batchResults.length}/${tasks.length})`);
    }
    
    // Clean up the temporary file
    if (process.env.SPRITE_TASK_FILE) {
      try {
        fs.unlinkSync(taskFilePath);
        console.log(`Removed temporary task file: ${taskFilePath}`);
      } catch (error) {
        console.error(`Error removing temporary file: ${error.message}`);
      }
    }
    
    // Final report
    console.log('\n=== Processing Complete ===');
    console.log(`Total: ${tasks.length} | Successful: ${results.successful} | Failed: ${results.failed}`);
    
    if (results.failed > 0) {
      console.log('\nFailed Tasks:');
      results.failedTasks.forEach((task, index) => {
        console.log(`${index + 1}. ${task.output}: ${task.error}`);
      });
    }
  } catch (error) {
    console.error('Error processing tasks:', error);
  }
  
  app.quit();
}
```

### 3. Benefits of This Implementation

- **Improved Performance**: Processing multiple sprite sheets concurrently
- **Controlled Resource Usage**: Limiting the number of concurrent operations
- **Better Error Handling**: Detailed error reporting without stopping the entire batch
- **Progress Tracking**: Clear indication of progress and estimated completion
- **Comprehensive Reporting**: Summary of successful and failed tasks

## Next Steps

1. Switch to Code mode to implement these changes
2. Test the implementation with a batch of sprite sheets
3. Fine-tune the batch size if needed based on performance