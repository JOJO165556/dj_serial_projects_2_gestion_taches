<script>
import axios from 'axios';
import task from "@/components/Task.vue";

export default {
  props:["tasks", "status"],

  methods: {
    async onDragEnd() {
      const updatedTasks = this.tasks.map((task, index) => ({
        id: task.id,
        position: index
      }));

      await axios.patch('/api/tasks/reorder/', {
        tasks: updatedTasks
      });
    }
  }
}
</script>