const { app } = require('electron');
const Spritesmith = require('spritesmith');
const fs = require('fs');
const { promisify } = require('util');
const spritesmithRun = promisify(Spritesmith.run);
const path = require('path');

// Check for task file path in command args or environment variable
const args = process.argv.slice(2);
const taskFileArg = args.find(arg => arg.startsWith('--taskfile='));
const taskFilePath = taskFileArg 
  ? taskFileArg.replace('--taskfile=', '') 
  : process.env.SPRITE_TASK_FILE;

if (!taskFilePath) {
  console.error('No task file specified. Use --taskfile=path or set SPRITE_TASK_FILE environment variable');
  app.quit();
  return;
}

console.log(`Reading tasks from: ${taskFilePath}`);

/**
 * Process a batch of tasks concurrently
 * @param {Array} tasks - Array of tasks to process
 * @param {number} startIndex - Starting index in the tasks array
 * @param {number} batchSize - Number of tasks to process in this batch
 * @param {number} totalTasks - Total number of tasks
 * @returns {Promise<Array>} - Results of the batch processing
 */
async function processBatch(tasks, startIndex, batchSize, totalTasks) {
  const endIndex = Math.min(startIndex + batchSize, tasks.length);
  const batch = tasks.slice(startIndex, endIndex);
  
  const batchPromises = batch.map(async (task, index) => {
    const taskIndex = startIndex + index;
    console.log(`[${taskIndex+1}/${totalTasks}] Processing: ${path.basename(task.output)}`);
    
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

/**
 * Main function to process all tasks with batching
 */
async function processTasks() {
  try {
    // Read the task file with improved error handling
    let tasksData;
    try {
      tasksData = fs.readFileSync(taskFilePath, 'utf8');
      
      // Check for and remove BOM if present
      if (tasksData.charCodeAt(0) === 0xFEFF) {
        console.log('Removing BOM from JSON file');
        tasksData = tasksData.slice(1);
      }
    } catch (error) {
      console.error(`Error reading task file: ${error.message}`);
      app.quit();
      return;
    }
    
    // Parse JSON with improved error handling
    let tasks;
    try {
      tasks = JSON.parse(tasksData);
    } catch (error) {
      console.error('Error parsing JSON:', error.message);
      
      // Show a preview of the file content for debugging
      console.error('File content preview:');
      console.error(tasksData.substring(0, 100) + '...');
      
      app.quit();
      return;
    }
    
    if (!Array.isArray(tasks)) {
      console.error('Invalid task file format: Expected an array of tasks');
      app.quit();
      return;
    }
    
    console.log(`Processing ${tasks.length} sprite sheets`);
    
    // Define batch size and track results
    const BATCH_SIZE = 10; // Process 6 tasks concurrently
    const results = {
      successful: 0,
      failed: 0,
      failedTasks: []
    };
    
    const startTime = Date.now();
    
    // Process in batches
    for (let i = 0; i < tasks.length; i += BATCH_SIZE) {
      const batchNumber = Math.floor(i / BATCH_SIZE) + 1;
      const totalBatches = Math.ceil(tasks.length / BATCH_SIZE);
      console.log(`\nProcessing batch ${batchNumber}/${totalBatches}`);
      
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
      const completedCount = Math.min(i + BATCH_SIZE, tasks.length);
      const completedPercentage = Math.round((completedCount / tasks.length) * 100);
      console.log(`Progress: ${completedPercentage}% (${completedCount}/${tasks.length})`);
      
      // Estimate time remaining if we have processed at least one batch
      if (batchNumber > 1) {
        const elapsedTime = Date.now() - startTime;
        const timePerTask = elapsedTime / completedCount;
        const tasksRemaining = tasks.length - completedCount;
        const estimatedTimeRemaining = Math.round((timePerTask * tasksRemaining) / 1000);
        
        if (estimatedTimeRemaining > 0) {
          console.log(`Estimated time remaining: ${estimatedTimeRemaining} seconds`);
        }
      }
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
    const totalTime = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log('\n=== Processing Complete ===');
    console.log(`Total time: ${totalTime} seconds`);
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

app.on('ready', processTasks);