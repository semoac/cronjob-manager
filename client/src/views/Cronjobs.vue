<template>
  <div>
    <b-alert v-model="showAlert" variant="info" dismissible>{{msg}}</b-alert>
    <b-container fluid>
      <b-row cols="12" class="m-3">
        <h2 class="m-3">Cronjob for namespace {{ namespace }}</h2>
        <b-spinner type="grow" label="Loading..." :hidden="loading"></b-spinner>
      </b-row>
      <b-row cols="12" class="m-3">
        <h3 class="m-3">Running Jobs</h3>
      </b-row>
      <b-row class="m-3">
        <b-col>
          <b-table
            :items="runningjobs"
            :fields="job_fields"
            hover
            small
            caption-top
            responsive
            head-variant="light"
          >
            <template v-slot:cell(status)="row">
              <b-badge :variant="getBadgeColor(row.value)">{{ row.value }}</b-badge>
            </template>
            <template v-slot:cell(started_at)="row">{{ row.value | formatDate }}</template>
            <template v-slot:cell(finished_at)="row">{{ row.value | formatDate }}</template>
            <template v-slot:cell(actions)="row">
              <b-button
                size="sm"
                @click="row.toggleDetails"
                class="mr-2"
              >{{ row.detailsShowing ? 'Hide' : 'Show'}} Details</b-button>
              <b-button
                size="sm"
                v-b-modal="'running-job-modal-' + row.item.name"
                class="mr-2"
              >Delete</b-button>
              <b-modal
                :id="'running-job-modal-' + row.item.name"
                title="Delete Job"
                @ok="deleteJob(row.item.name)"
              >
                <p class="my-4">
                  Delete
                  <b>{{row.item.name}}?</b>
                </p>
              </b-modal>
            </template>
            <template v-slot:row-details="row">
              <b-card>
                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Name:</b>
                  </b-col>
                  <b-col>{{ row.item.name }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Status:</b>
                  </b-col>
                  <b-col>{{ row.item.status }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Retry limit:</b>
                  </b-col>
                  <b-col>{{ row.item.retry_limit }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Timeout:</b>
                  </b-col>
                  <b-col>{{ row.item.timeout_limit }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Failed executions:</b>
                  </b-col>
                  <b-col>{{ row.item.failure_count }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Containers:</b>
                  </b-col>
                  <b-col>
                    <b-list-group>
                      <b-list-group-item v-for="pod in row.item.pods" :key="pod.name">
                        <b-link
                          target="_blank"
                          :href="'https://app.datadoghq.com/logs?query=kube_namespace%3A' + namespace + '+pod_name%3A' + pod.name"
                        >{{ pod.name }}</b-link>
                        ({{ pod.phase }})
                      </b-list-group-item>
                    </b-list-group>
                  </b-col>
                </b-row>

                <b-button size="sm" @click="row.toggleDetails">Hide Details</b-button>
              </b-card>
            </template>
          </b-table>
        </b-col>
      </b-row>

      <b-row cols="12" class="m-3">
        <h3 class="m-3">Cronjob list</h3>
      </b-row>
      <b-row class="m-3" v-for="(cronjob,index) in cronjobs" :key="index">
        <b-col>
          <b-table
            :items="getJobItems(cronjob.jobs)"
            :fields="job_fields"
            hover
            small
            caption-top
            responsive
            head-variant="light"
          >
            <template v-slot:table-caption>
              <h3>{{ cronjob.name }}</h3>
              <b-card>
                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-left">
                    <b>Schedule</b>
                  </b-col>
                  <b-col>{{ cronjob.schedule | formatCron }} (UTC)</b-col>
                </b-row>
                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-left">
                    <b>Action:</b>
                  </b-col>
                  <b-col>
                    <b-button
                      size="sm"
                      class="mr-2"
                      :variant="cronjob.suspended == true ? 'danger' : 'info'"
                      v-b-modal="'cronjob-modal-' + cronjob.name"
                    >{{ cronjob.suspended == true ? 'Enable' : 'Disable'}}</b-button>
                    <b-button
                      size="sm"
                      variant="primary"
                      v-b-modal="'trigger-modal-' + cronjob.name"
                    >Run now!</b-button>
                  </b-col>
                </b-row>
              </b-card>
              <b-modal
                :id="'cronjob-modal-' + cronjob.name"
                title="Confirmation"
                @ok="changeCronjobSuspend(cronjob.name,index)"
              >
                <p class="my-4">
                  Are you ready to confirm this action over
                  <b>{{cronjob.name}}</b>?
                </p>
              </b-modal>
              <b-modal
                :id="'trigger-modal-' + cronjob.name"
                title="Trigger a job"
                @ok="triggerJob(cronjob.name)"
              >
                <p class="my-4">
                  A new job will be launched from the current cronjob configuration.
                  Are you sure?
                </p>
              </b-modal>
            </template>
            <template v-slot:cell(status)="row">
              <b-badge :variant="getBadgeColor(row.value)">{{ row.value }}</b-badge>
            </template>
            <template v-slot:cell(started_at)="row">{{ row.value | formatDate }}</template>
            <template v-slot:cell(finished_at)="row">{{ row.value | formatDate }}</template>
            <template v-slot:cell(actions)="row">
              <b-button
                size="sm"
                @click="row.toggleDetails"
                class="mr-2"
              >{{ row.detailsShowing ? 'Hide' : 'Show'}} Details</b-button>
              <b-button size="sm" v-b-modal="'job-modal-' + row.item.name" class="mr-2">Delete</b-button>
              <b-modal
                :id="'job-modal-' + row.item.name"
                title="Delete Job"
                @ok="deleteJob(row.item.name)"
              >
                <p class="my-4">
                  Delete
                  <b>{{row.item.name}}?</b>
                </p>
              </b-modal>
            </template>

            <template v-slot:row-details="row">
              <b-card>
                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Name:</b>
                  </b-col>
                  <b-col>{{ row.item.name }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Status:</b>
                  </b-col>
                  <b-col>{{ row.item.status }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Retry limit:</b>
                  </b-col>
                  <b-col>{{ row.item.retry_limit }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Timeout:</b>
                  </b-col>
                  <b-col>{{ row.item.timeout_limit }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Failed executions:</b>
                  </b-col>
                  <b-col>{{ row.item.failure_count }}</b-col>
                </b-row>

                <b-row class="mb-2">
                  <b-col sm="3" class="text-sm-right">
                    <b>Containers:</b>
                  </b-col>
                  <b-col>
                    <b-list-group>
                      <b-list-group-item v-for="pod in row.item.pods" :key="pod.name">
                        <b-link
                          target="_blank"
                          :href="'https://app.datadoghq.com/logs?query=kube_namespace%3A' + namespace + '+pod_name%3A' + pod.name"
                        >{{ pod.name }}</b-link>
                        ({{ pod.phase }})
                      </b-list-group-item>
                    </b-list-group>
                  </b-col>
                </b-row>

                <b-button size="sm" @click="row.toggleDetails">Hide Details</b-button>
              </b-card>
            </template>
          </b-table>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Cronjobs",
  props: {
    namespace: String
  },
  data() {
    return {
      cronjobs: [],
      runningjobs: [],
      job_fields: ["name", "status", "started_at", "finished_at", "actions"],
      showAlert: false,
      msg: "No problems",
      loading: false
    };
  },
  methods: {
    getCronjobs() {
      const path =
        process.env.VUE_APP_URL + "/api/v1/cronjobs/" + this.namespace;
      this.loading = false;
      axios
        .get(path)
        .then(res => {
          this.cronjobs = res.data.cronjobs;
          this.getRunningJobs();
          if (res.status >= 400) {
            this.msg = res.statusText;
            this.showAlert = true;
          }
          this.loading = true;
        })
        .catch(error => {
          this.msg = error;
          this.showAlert = true;
        });
    },
    getRunningJobs() {
      var result = [];
      for (const cronjob of this.cronjobs) {
        for (const job of cronjob.jobs) {
          for (const pod of job.pods) {
            if (pod.phase == "Running") {
              result.push({
                name: job.name,
                status: "Running",
                started_at: job.start_at,
                finished_at: job.finish_at,
                retry_limit: job.backoff_limit,
                timeout_limit: job.deadline_seconds,
                failure_count: job.failure_count,
                pods: job.pods
              });
            }
          }
        }
      }
      this.runningjobs = result;
    },
    getJobItems: function(jobs) {
      var status;
      var result = [];
      for (const job of jobs) {
        if (job.success_count > 0) {
          status = "Finished";
        } else if (job.active == true) {
          status = "Running";
        } else if (job.failure_count > 0) {
          status = "Failed";
        } else {
          status = "Failed";
        }
        result.push({
          name: job.name,
          status: status,
          started_at: job.start_at,
          finished_at: job.finish_at,
          retry_limit: job.backoff_limit,
          timeout_limit: job.deadline_seconds,
          failure_count: job.failure_count,
          pods: job.pods
        });
      }
      return result;
    },
    getBadgeColor: function(status) {
      var color;
      switch (status) {
        case "Running":
          color = "primary";
          break;
        case "Finished":
          color = "success";
          break;
        case "Failed":
          color = "danger";
          break;
        default:
          color = "info";
      }
      return color;
    },
    changeCronjobSuspend: function(cj, i) {
      const path =
        process.env.VUE_APP_URL +
        "/api/v1/cronjobs/" +
        this.namespace +
        "/" +
        cj;
      this.loading = false;
      this.msg = "Sending request...";
      this.makeToast();
      axios
        .patch(path)
        .then(data => {
          this.loading = true;
          this.cronjobs[i].suspended = !this.cronjobs[i].suspended;
          if (data.status >= 400) {
            this.msg = data.statusText;
            this.showAlert = true;
          } else {
            this.msg =
              "The status for the  " +
              cj +
              " has been set to Enabled=" +
              !this.cronjobs[i].suspended;
          }
          this.makeToast();
        })
        .catch(error => {
          this.msg = error;
          this.showAlert = true;
        });
      return;
    },
    deleteJob: function(j) {
      const path =
        process.env.VUE_APP_URL + "/api/v1/job/" + this.namespace + "/" + j;
      this.msg = "Sending request...";
      this.makeToast();
      axios
        .delete(path)
        .then(data => {
          if (data.status >= 400) {
            this.msg = data.statusText;
            this.showAlert = true;
          } else {
            this.msg =
              "Job " +
              j +
              " and its containers has been scheduled for termination and removal.";
          }
          this.makeToast();
          this.getCronjobs();
        })
        .catch(error => {
          this.msg = error;
          this.showAlert = true;
        });
    },
    triggerJob: function(cj) {
      const path =
        process.env.VUE_APP_URL + "/api/v1/job/" + this.namespace + "/" + cj;
      this.loading = false;
      this.msg = "Sending request...";
      this.makeToast();
      axios
        .put(path)
        .then(data => {
          if (data.status >= 400) {
            this.msg = data.statusText;
            this.showAlert = true;
          } else {
            this.msg =
              "A manual run as been scheduled for cronjob " +
              cj +
              ". Please reload the page after a few seconds.";
          }
          this.getCronjobs();
          this.makeToast();
        })
        .catch(error => {
          this.msg = error;
          this.showAlert = true;
        });
    },
    makeToast: function() {
      this.$bvToast.toast(this.msg, {
        title: "Information",
        variant: "info",
        solid: true,
        appendToast: true
      });
    }
  },
  computed: {},
  created() {
    document.title = "Cronjob Manager - Jobs and Containers";
    this.getCronjobs();
  }
};
</script>