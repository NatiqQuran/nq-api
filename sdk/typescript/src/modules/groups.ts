import * as GroupsType from "../types/groups";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class GroupsController extends BaseController {

    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** GET /groups/ */
    async list(config?: RequestConfig
    ): Promise<AxiosResponse<GroupsType.GroupsListResponseData>> {
        return await this.axiosGet(`/groups/`, config);
    }
    
    /** POST /groups/ */
    async create(data: GroupsType.GroupsCreateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<GroupsType.GroupsCreateResponseData>> {
        return await this.axiosPost(`/groups/`, data, config);
    }
    
    /** GET /groups/{id}/ */
    async retrieve(id: string, config?: RequestConfig
    ): Promise<AxiosResponse<GroupsType.GroupsRetrieveResponseData>> {
        return await this.axiosGet(`/groups/${id}/`, config);
    }
    
    /** PUT /groups/{id}/ */
    async update(id: string, data: GroupsType.GroupsUpdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<GroupsType.GroupsUpdateResponseData>> {
        return await this.axiosPut(`/groups/${id}/`, data, config);
    }
    
    /** PATCH /groups/{id}/ */
    async partialUpdate(id: string, data: GroupsType.GroupsPartialupdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<GroupsType.GroupsPartialupdateResponseData>> {
        return await this.axiosPatch(`/groups/${id}/`, data, config);
    }
    
    /** DELETE /groups/{id}/ */
    async delete(id: string, config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/groups/${id}/`, config);
    }
    
}